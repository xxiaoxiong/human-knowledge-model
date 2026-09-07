"""Loopback-only HTTP service for the HKM Python Codex problem studio."""

from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import time
import uuid
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import unquote, urlsplit

from . import __version__
from .agent import CodexAgent
from .graph import (
    Graph,
    create_deterministic_analysis,
    ground_analysis,
    load_graph,
    public_retrieval,
    retrieve_graph_context,
)
from .prompt import build_prompt
from .settings import ConfigurationError, ROOT, Settings, load_settings


STATIC_ROOT = ROOT / "dist-site"
MAX_BODY_BYTES = 1_000_000
MAX_ACTIVE_RUNS = 2
SESSION_TTL_SECONDS = 2 * 60 * 60
FORBIDDEN_BROWSER_CONFIG = {
    "provider",
    "apiKey",
    "api_key",
    "baseUrl",
    "base_url",
    "model",
    "modelId",
    "model_id",
    "reasoningEffort",
}


class BusyError(RuntimeError):
    pass


class ClientDisconnected(RuntimeError):
    pass


@dataclass(slots=True)
class SessionState:
    thread: Any = None
    active_turn: Any = None
    touched_at: float = field(default_factory=time.time)
    run_lock: threading.Lock = field(default_factory=threading.Lock)


class AgentService:
    def __init__(self, settings: Settings, graph: Graph | None = None) -> None:
        self.settings = settings
        self.graph = graph or load_graph()
        self.agent = None if settings.mock else CodexAgent(settings)
        self.sessions: dict[str, SessionState] = {}
        self.sessions_lock = threading.Lock()
        self.capacity = threading.BoundedSemaphore(MAX_ACTIVE_RUNS)

    def _expire_sessions(self) -> None:
        cutoff = time.time() - SESSION_TTL_SECONDS
        with self.sessions_lock:
            expired = [
                session_id
                for session_id, session in self.sessions.items()
                if session.touched_at < cutoff and session.active_turn is None
            ]
            for session_id in expired:
                self.sessions.pop(session_id, None)

    def _session(self, requested_id: str) -> tuple[str, SessionState]:
        self._expire_sessions()
        with self.sessions_lock:
            if requested_id and requested_id in self.sessions:
                return requested_id, self.sessions[requested_id]
            session_id = str(uuid.uuid4())
            session = SessionState()
            self.sessions[session_id] = session
            return session_id, session

    def analyze(
        self,
        *,
        query: str,
        requested_session_id: str,
        conversation: list[dict[str, str]],
        emit: Callable[[dict[str, Any]], None],
    ) -> None:
        if not self.capacity.acquire(blocking=False):
            raise BusyError("当前已有两个分析在运行，请稍后重试。")
        session_id, session = self._session(requested_session_id)
        retrieval = retrieve_graph_context(self.graph, "\n".join([*(item["content"] for item in conversation), query]))
        try:
            emit(
                {
                    "type": "session",
                    "sessionId": session_id,
                    "agent": self.settings.public_summary(),
                }
            )
            emit(
                {
                    "type": "progress",
                    "stage": "retrieve",
                    "message": "已从完整图谱检索问题原型、领域骨架与跨学科模型",
                }
            )
            emit({"type": "retrieval", "data": public_retrieval(retrieval)})

            with session.run_lock:
                if self.settings.mock:
                    emit(
                        {
                            "type": "progress",
                            "stage": "decompose",
                            "message": "正在生成可复查的问题结构",
                        }
                    )
                    raw_analysis = create_deterministic_analysis(self.graph, retrieval, query)
                    usage = None
                else:
                    if session.thread is None:
                        session.thread = self.agent.new_thread()
                    emit(
                        {
                            "type": "progress",
                            "stage": "decompose",
                            "message": "Codex 正在定义边界并递归分解子问题",
                        }
                    )

                    def remember_turn(turn: Any) -> None:
                        session.active_turn = turn

                    raw_analysis, usage = self.agent.run_turn(
                        session.thread,
                        build_prompt(query=query, retrieval=retrieval, conversation=conversation),
                        on_progress=lambda stage, message: emit(
                            {"type": "progress", "stage": stage, "message": message}
                        ),
                        on_turn=remember_turn,
                    )
                    session.active_turn = None

                emit(
                    {
                        "type": "progress",
                        "stage": "ground",
                        "message": "正在校验图谱节点、关系与行动门",
                    }
                )
                analysis = ground_analysis(self.graph, retrieval, raw_analysis, query)
                session.touched_at = time.time()
                emit(
                    {
                        "type": "final",
                        "sessionId": session_id,
                        "analysis": analysis,
                        "usage": usage,
                    }
                )
        except ClientDisconnected:
            self.stop(session_id)
        finally:
            session.active_turn = None
            self.capacity.release()

    def stop(self, session_id: str) -> bool:
        with self.sessions_lock:
            session = self.sessions.get(session_id)
        turn = session.active_turn if session else None
        if turn is None:
            return False
        try:
            turn.interrupt()
            return True
        except Exception:
            return False

    def reset(self, session_id: str) -> None:
        self.stop(session_id)
        with self.sessions_lock:
            self.sessions.pop(session_id, None)

    def close(self) -> None:
        if self.agent:
            self.agent.close()


def _allowed_host(value: str) -> bool:
    host = (value or "").strip().lower()
    if host.startswith("["):
        return host.startswith("[::1]")
    return host.split(":", 1)[0] in {"127.0.0.1", "localhost"}


def _safe_error(error: BaseException, settings: Settings) -> str:
    message = str(error or "分析失败。")[:1000]
    if settings.api_key:
        message = message.replace(settings.api_key, "[redacted]")
    return message


def _handler(service: AgentService):
    class Handler(BaseHTTPRequestHandler):
        server_version = "HKMProblemStudio/0.10"

        def log_message(self, format: str, *args: Any) -> None:
            # Keep access logs credential-free. Request bodies are never logged.
            super().log_message(format, *args)

        def _security_headers(self) -> None:
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")

        def _json(self, status: int, value: dict[str, Any]) -> None:
            body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self._security_headers()
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict[str, Any]:
            raw_length = self.headers.get("Content-Length", "0")
            try:
                length = int(raw_length)
            except ValueError as exc:
                raise ValueError("无效的 Content-Length。") from exc
            if length < 0 or length > MAX_BODY_BYTES:
                raise ValueError("请求内容过大。")
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            if not isinstance(payload, dict):
                raise ValueError("请求体必须是 JSON object。")
            return payload

        def _request_allowed(self) -> bool:
            if _allowed_host(self.headers.get("Host", "")):
                return True
            self._json(421, {"error": "该服务只接受本机同源请求。"})
            return False

        def do_GET(self) -> None:
            if not self._request_allowed():
                return
            path = urlsplit(self.path).path
            if path == "/api/health":
                self._json(
                    200,
                    {
                        "ok": True,
                        "service": "hkm-python-agent",
                        "mode": "mock" if service.settings.mock else "live",
                        "version": __version__,
                        "runtime": "openai-codex",
                        "agent": service.settings.public_summary(),
                        "security": {
                            "bind": "loopback",
                            "config": "environment-only",
                            "browserSecrets": False,
                            "sandbox": "read-only",
                            "approvals": "deny-all",
                            "threadPersistence": "ephemeral",
                        },
                    },
                )
                return
            if path.startswith("/api/"):
                self._json(404, {"error": "Unknown API route"})
                return
            self._serve_static(path)

        def _serve_static(self, request_path: str) -> None:
            relative = unquote(request_path or "/")
            if relative == "/":
                relative = "/index.html"
            target = (STATIC_ROOT / relative.lstrip("/")).resolve()
            try:
                target.relative_to(STATIC_ROOT.resolve())
            except ValueError:
                self._json(403, {"error": "Forbidden"})
                return
            if not target.is_file():
                self._json(404, {"error": "Not found"})
                return
            body = target.read_bytes()
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            if content_type.startswith("text/") or content_type in {"application/json", "application/xml"}:
                content_type += "; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header(
                "Cache-Control",
                "no-cache" if target.name == "model.json" else "public, max-age=300",
            )
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; connect-src 'self'; img-src 'self' data:; "
                "style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; "
                "base-uri 'self'; frame-ancestors 'none'",
            )
            self._security_headers()
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            if not self._request_allowed():
                return
            path = urlsplit(self.path).path
            try:
                body = self._read_json()
                if path == "/api/session/reset":
                    service.reset(str(body.get("sessionId") or ""))
                    self._json(200, {"ok": True})
                    return
                if path == "/api/session/stop":
                    stopped = service.stop(str(body.get("sessionId") or ""))
                    self._json(200, {"ok": True, "stopped": stopped})
                    return
                if path == "/api/analyze":
                    self._analyze(body)
                    return
                self._json(404, {"error": "Unknown API route"})
            except (ValueError, json.JSONDecodeError) as error:
                self._json(400, {"error": _safe_error(error, service.settings)})

        def _analyze(self, body: dict[str, Any]) -> None:
            forbidden = sorted(FORBIDDEN_BROWSER_CONFIG.intersection(body))
            if forbidden:
                self._json(
                    400,
                    {"error": "模型配置只能在服务启动时从 .env 注入，浏览器请求不得覆盖。"},
                )
                return
            query = str(body.get("query") or "").strip()
            if not 4 <= len(query) <= 4000:
                self._json(400, {"error": "问题长度需要在 4–4000 个字符之间。"})
                return
            raw_conversation = body.get("conversation") if isinstance(body.get("conversation"), list) else []
            conversation = []
            for item in raw_conversation[-4:]:
                if not isinstance(item, dict):
                    continue
                content = str(item.get("content") or "").strip()[:2000]
                if content:
                    conversation.append(
                        {
                            "role": "assistant" if item.get("role") == "assistant" else "user",
                            "content": content,
                        }
                    )

            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self._security_headers()
            self.end_headers()

            def emit(event: dict[str, Any]) -> None:
                try:
                    line = json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
                    self.wfile.write(line.encode("utf-8"))
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError) as exc:
                    raise ClientDisconnected() from exc

            try:
                service.analyze(
                    query=query,
                    requested_session_id=str(body.get("sessionId") or ""),
                    conversation=conversation,
                    emit=emit,
                )
            except BusyError as error:
                emit({"type": "error", "error": str(error), "recoverable": True})
            except ClientDisconnected:
                return
            except Exception as error:
                try:
                    emit(
                        {
                            "type": "error",
                            "error": _safe_error(error, service.settings),
                            "recoverable": True,
                        }
                    )
                except ClientDisconnected:
                    return

    return Handler


class HKMServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, settings: Settings, graph: Graph | None = None) -> None:
        self.service = AgentService(settings, graph)
        super().__init__((settings.host, settings.port), _handler(self.service))

    def server_close(self) -> None:
        self.service.close()
        super().server_close()


def create_server(settings: Settings, graph: Graph | None = None) -> HKMServer:
    return HKMServer(settings, graph)


def start_server(settings: Settings) -> None:
    server = create_server(settings)
    host, port = server.server_address[:2]
    mode = "mock" if settings.mock else f"{settings.provider_name} · {settings.model_id}"
    print(f"HKM Python Agent ready at http://{host}:{port} ({mode})")
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the HKM Python Codex problem studio")
    parser.add_argument("--mock", action="store_true", help="run without calling a model")
    args = parser.parse_args()
    try:
        settings = load_settings(force_mock=args.mock)
    except ConfigurationError as error:
        parser.error(str(error))
    start_server(settings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
