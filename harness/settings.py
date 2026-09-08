"""Startup-only configuration for the HKM agent service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}
HOSTED_BIND_HOSTS = {"0.0.0.0", "::"}
REASONING_EFFORTS = {"minimal", "low", "medium", "high", "xhigh", "max"}


class ConfigurationError(ValueError):
    """Raised when startup configuration is missing or unsafe."""


@dataclass(frozen=True, slots=True)
class Settings:
    host: str
    port: int
    mock: bool
    provider_name: str
    base_url: str
    api_key: str
    model_id: str
    reasoning_effort: str | None
    deployment_mode: str = "local"
    public_origin: str = ""
    access_token: str = ""
    runtime_dir: Path = ROOT / ".hkm-runtime"

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, str],
        *,
        force_mock: bool = False,
    ) -> "Settings":
        deployment_mode = values.get("HKM_DEPLOYMENT_MODE", "local").strip().lower()
        if deployment_mode not in {"local", "hosted"}:
            raise ConfigurationError("HKM_DEPLOYMENT_MODE 只能是 local 或 hosted。")

        default_host = "0.0.0.0" if deployment_mode == "hosted" else "127.0.0.1"
        host = values.get("HKM_HOST", default_host).strip()
        allowed_bind_hosts = HOSTED_BIND_HOSTS if deployment_mode == "hosted" else LOOPBACK_HOSTS
        if host not in allowed_bind_hosts:
            allowed = "0.0.0.0 或 ::" if deployment_mode == "hosted" else "localhost、127.0.0.1 或 ::1"
            raise ConfigurationError(f"{deployment_mode} 模式下 HKM_HOST 只允许绑定 {allowed}。")

        try:
            port = int(values.get("PORT") or values.get("HKM_PORT", "4317"))
        except ValueError as exc:
            raise ConfigurationError("HKM_PORT 必须是整数。") from exc
        if not 1 <= port <= 65535:
            raise ConfigurationError("HKM_PORT 必须在 1 到 65535 之间。")

        mode = values.get("HKM_AGENT_MODE", "live").strip().lower()
        if mode not in {"live", "mock"}:
            raise ConfigurationError("HKM_AGENT_MODE 只能是 live 或 mock。")
        mock = force_mock or mode == "mock"

        provider_name = values.get("HKM_MODEL_PROVIDER_NAME", "Environment model").strip()
        base_url = values.get("HKM_MODEL_BASE_URL", "").strip().rstrip("/")
        api_key = values.get("HKM_MODEL_API_KEY", "").strip()
        model_id = values.get("HKM_MODEL_ID", "").strip()
        effort = values.get("HKM_MODEL_REASONING_EFFORT", "").strip().lower() or None
        access_token = values.get("HKM_ACCESS_TOKEN", "").strip()
        public_origin = values.get("HKM_PUBLIC_ORIGIN", "").strip().rstrip("/")
        render_hostname = values.get("RENDER_EXTERNAL_HOSTNAME", "").strip().lower()
        if not public_origin and render_hostname:
            public_origin = f"https://{render_hostname}"
        runtime_value = values.get("HKM_RUNTIME_DIR", "").strip() or str(ROOT / ".hkm-runtime")
        runtime_dir = Path(runtime_value).expanduser()

        if effort and effort not in REASONING_EFFORTS:
            allowed = ", ".join(sorted(REASONING_EFFORTS))
            raise ConfigurationError(f"HKM_MODEL_REASONING_EFFORT 必须为空或以下值之一：{allowed}。")

        if not mock:
            required = {
                "HKM_MODEL_BASE_URL": base_url,
                "HKM_MODEL_API_KEY": api_key,
                "HKM_MODEL_ID": model_id,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ConfigurationError(f"缺少启动配置：{', '.join(missing)}。请先配置 .env。")
            parsed = urlparse(base_url)
            if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
                raise ConfigurationError("HKM_MODEL_BASE_URL 必须是无内嵌凭据的 HTTPS 地址。")

        if deployment_mode == "hosted":
            if len(access_token) < 32:
                raise ConfigurationError("hosted 模式必须配置至少 32 个字符的 HKM_ACCESS_TOKEN。")
            parsed_origin = urlparse(public_origin)
            if (
                parsed_origin.scheme != "https"
                or not parsed_origin.netloc
                or parsed_origin.username
                or parsed_origin.password
                or parsed_origin.path not in {"", "/"}
                or parsed_origin.query
                or parsed_origin.fragment
            ):
                raise ConfigurationError(
                    "hosted 模式必须配置无路径、无凭据的 HTTPS HKM_PUBLIC_ORIGIN。"
                )

        return cls(
            host=host,
            port=port,
            mock=mock,
            provider_name=provider_name or "Environment model",
            base_url=base_url,
            api_key=api_key,
            model_id=model_id,
            reasoning_effort=effort,
            deployment_mode=deployment_mode,
            public_origin=public_origin,
            access_token=access_token,
            runtime_dir=runtime_dir,
        )

    @property
    def configured(self) -> bool:
        return self.mock or bool(self.base_url and self.api_key and self.model_id)

    @property
    def hosted(self) -> bool:
        return self.deployment_mode == "hosted"

    def public_summary(self) -> dict[str, object]:
        return {
            "source": "environment",
            "provider": self.provider_name if not self.mock else "Deterministic demo",
            "model": self.model_id if not self.mock else "mock",
            "configured": self.configured,
        }


def load_settings(*, force_mock: bool = False) -> Settings:
    """Load .env once at process startup, while preserving injected env values."""

    load_dotenv(ROOT / ".env", override=False)
    return Settings.from_mapping(os.environ, force_mock=force_mock)
