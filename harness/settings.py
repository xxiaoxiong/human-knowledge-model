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

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[str, str],
        *,
        force_mock: bool = False,
    ) -> "Settings":
        host = values.get("HKM_HOST", "127.0.0.1").strip()
        if host not in LOOPBACK_HOSTS:
            raise ConfigurationError("HKM_HOST 只允许绑定 localhost、127.0.0.1 或 ::1。")

        try:
            port = int(values.get("HKM_PORT", "4317"))
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

        return cls(
            host=host,
            port=port,
            mock=mock,
            provider_name=provider_name or "Environment model",
            base_url=base_url,
            api_key=api_key,
            model_id=model_id,
            reasoning_effort=effort,
        )

    @property
    def configured(self) -> bool:
        return self.mock or bool(self.base_url and self.api_key and self.model_id)

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
