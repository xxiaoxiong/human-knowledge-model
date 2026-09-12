"""Official OpenAI Codex Python SDK integration for the HKM problem studio."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from typing import Any, Callable

from openai_codex import ApprovalMode, Codex, CodexConfig, Sandbox

from .analysis_schema import ANALYSIS_SCHEMA
from .prompt import BASE_INSTRUCTIONS, DEVELOPER_INSTRUCTIONS
from .settings import ROOT, Settings


ProgressCallback = Callable[[str, str], None]


def _toml_string(value: str) -> str:
    """JSON strings are valid TOML basic strings and safely quote user values."""

    return json.dumps(value, ensure_ascii=False)


def codex_config(settings: Settings) -> CodexConfig:
    """Create a provider configuration without placing the credential in CLI args."""

    runtime_home = settings.runtime_dir / "codex-home"
    runtime_home.mkdir(parents=True, exist_ok=True)
    workspace = ROOT / "harness" / "workspace"
    safe_shell_environment = [
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "PATHEXT",
        "PATH",
        "TEMP",
        "TMP",
        "USERPROFILE",
        "APPDATA",
        "LOCALAPPDATA",
        "HOME",
        "SHELL",
        "LANG",
        "LC_ALL",
    ]
    overrides = (
        'model_provider="hkm_env"',
        f"model_providers.hkm_env.name={_toml_string(settings.provider_name)}",
        f"model_providers.hkm_env.base_url={_toml_string(settings.base_url)}",
        'model_providers.hkm_env.env_key="HKM_MODEL_API_KEY"',
        'model_providers.hkm_env.wire_api="responses"',
        "model_providers.hkm_env.request_max_retries=1",
        "model_providers.hkm_env.stream_max_retries=1",
        "model_providers.hkm_env.stream_idle_timeout_ms=180000",
        'web_search="disabled"',
        'history.persistence="none"',
        "mcp_servers={}",
        "features.shell_tool=false",
        "features.view_image=false",
        "features.multi_agent=false",
        "features.multi_agent_v2=false",
        "features.apps=false",
        "features.plugins=false",
        "features.tool_suggest=false",
        "features.image_generation=false",
        "features.goals=false",
        "features.hooks=false",
        # Agnes rejects a tool_choice field when the tool list is empty. Keep the
        # harmless in-memory planning function as the sole standard function tool.
        "tools.update_plan.enabled=true",
        "tools.experimental_request_user_input.enabled=false",
        "orchestrator.skills.enabled=false",
        "orchestrator.mcp.enabled=false",
        "include_permissions_instructions=false",
        "include_apps_instructions=false",
        "include_collaboration_mode_instructions=false",
        "include_environment_context=false",
        f"shell_environment_policy.include_only={json.dumps(safe_shell_environment)}",
    )
    return CodexConfig(
        cwd=str(workspace),
        config_overrides=overrides,
        env={
            "CODEX_HOME": str(runtime_home),
            "CODEX_APP_SERVER_DISABLE_MANAGED_CONFIG": "1",
            "HKM_MODEL_API_KEY": settings.api_key,
            "RUST_LOG": "error",
        },
        client_name="hkm_problem_studio",
        client_title="Human Knowledge Model Problem Studio",
    )


def parse_analysis(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    text = str(value or "").strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3].rstrip()
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("模型返回的结构化结果不是 JSON object。")
    return parsed


def _extract_response_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct
    chunks: list[str] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content") or []:
            if isinstance(content, dict) and content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
    return "\n".join(chunks).strip()


def _is_input_format_error(error: Exception) -> bool:
    text = str(error).lower()
    return (
        "400" in text
        and "input" in text
        and ("invalid" in text or "validation" in text or "deserialize" in text)
    )


class CodexAgent:
    """Long-lived SDK client with ephemeral, in-memory conversation threads."""

    def __init__(self, settings: Settings) -> None:
        if settings.mock:
            raise ValueError("Mock mode does not create a Codex runtime.")
        self.settings = settings
        self._client: Codex | None = None
        self._client_lock = threading.Lock()
        self._responses_string_input = False

    def _get_client(self) -> Codex:
        with self._client_lock:
            if self._client is None:
                self._client = Codex(config=codex_config(self.settings))
            return self._client

    def new_thread(self):
        client = self._get_client()
        return client.thread_start(
            approval_mode=ApprovalMode.deny_all,
            base_instructions=BASE_INSTRUCTIONS,
            cwd=str(ROOT / "harness" / "workspace"),
            developer_instructions=DEVELOPER_INSTRUCTIONS,
            ephemeral=True,
            model=self.settings.model_id,
            model_provider="hkm_env",
            sandbox=Sandbox.read_only,
        )

    def run_turn(
        self,
        thread,
        prompt: str,
        *,
        on_progress: ProgressCallback | None = None,
        on_turn: Callable[[Any], None] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        if self._responses_string_input:
            return self._run_direct_response(prompt, on_progress=on_progress)
        try:
            return self._run_codex_turn(
                thread,
                prompt,
                on_progress=on_progress,
                on_turn=on_turn,
            )
        except RuntimeError as error:
            if not _is_input_format_error(error):
                raise
            self._responses_string_input = True
            return self._run_direct_response(prompt, on_progress=on_progress)

    def _run_codex_turn(
        self,
        thread,
        prompt: str,
        *,
        on_progress: ProgressCallback | None = None,
        on_turn: Callable[[Any], None] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        kwargs: dict[str, Any] = {
            "approval_mode": ApprovalMode.deny_all,
            "output_schema": ANALYSIS_SCHEMA,
            "sandbox": Sandbox.read_only,
        }
        if self.settings.reasoning_effort:
            kwargs["effort"] = self.settings.reasoning_effort

        turn = thread.turn(prompt, **kwargs)
        if on_turn:
            on_turn(turn)
        final_response: str | None = None
        usage: dict[str, Any] | None = None
        completed: dict[str, Any] | None = None
        reasoning_reported = False

        for event in turn.stream():
            payload = event.payload
            data = payload.model_dump(mode="json", by_alias=True) if hasattr(payload, "model_dump") else {}
            if event.method == "item/completed":
                item = data.get("item") or {}
                if item.get("type") == "reasoning" and not reasoning_reported:
                    reasoning_reported = True
                    if on_progress:
                        on_progress("reason", "正在比较机制、约束与候选路径")
                if item.get("type") == "agentMessage" and item.get("text"):
                    if item.get("phase") in {None, "finalAnswer", "final_answer"}:
                        final_response = item["text"]
            elif event.method == "thread/tokenUsage/updated":
                usage = data.get("tokenUsage")
            elif event.method == "turn/completed":
                completed = data.get("turn") or {}

        if completed and completed.get("status") == "failed":
            error = completed.get("error") or {}
            raise RuntimeError(error.get("message") or "Codex turn failed.")
        if not final_response:
            raise RuntimeError("模型没有返回结构化分析结果。")
        return parse_analysis(final_response), usage

    def _run_direct_response(
        self,
        prompt: str,
        *,
        on_progress: ProgressCallback | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        """Fallback for Responses providers that only accept a string input."""

        if on_progress:
            on_progress("reason", "模型提供方正在以 Responses 兼容模式生成分析")
        request_payload = {
            "model": self.settings.model_id,
            "input": f"{BASE_INSTRUCTIONS}\n\n{DEVELOPER_INSTRUCTIONS}\n\n{prompt}",
            "stream": False,
            "max_output_tokens": 12000,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "hkm_analysis",
                    "strict": True,
                    "schema": ANALYSIS_SCHEMA,
                }
            },
        }
        request = urllib.request.Request(
            f"{self.settings.base_url}/responses",
            data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "hkm-problem-studio/0.11",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")[:2000]
            raise RuntimeError(f"Responses compatibility request failed ({error.code}): {body}") from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise RuntimeError(f"Responses compatibility request failed: {error}") from error
        if not isinstance(payload, dict):
            raise RuntimeError("Responses compatibility result is not a JSON object.")
        output_text = _extract_response_text(payload)
        if not output_text:
            raise RuntimeError("Responses compatibility result did not contain output text.")
        usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else None
        return parse_analysis(output_text), usage

    def close(self) -> None:
        with self._client_lock:
            if self._client is not None:
                self._client.close()
                self._client = None


def config_contains_secret(settings: Settings) -> bool:
    """Test helper: provider CLI overrides must never contain the credential."""

    config = codex_config(settings)
    return any(settings.api_key in value for value in config.config_overrides)
