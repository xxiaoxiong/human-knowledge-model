from __future__ import annotations

import json
import unittest

from openai_codex import Codex, CodexConfig

from harness.agent import codex_config, config_contains_secret
from harness.settings import ConfigurationError, Settings


class SettingsTests(unittest.TestCase):
    def live_settings(self) -> Settings:
        return Settings.from_mapping(
            {
                "HKM_HOST": "127.0.0.1",
                "HKM_PORT": "4317",
                "HKM_MODEL_PROVIDER_NAME": "Test provider",
                "HKM_MODEL_BASE_URL": "https://example.com/v1",
                "HKM_MODEL_API_KEY": "unit-test-secret",
                "HKM_MODEL_ID": "test-model",
            }
        )

    def test_official_python_sdk_is_importable(self) -> None:
        self.assertTrue(callable(Codex))
        self.assertTrue(callable(CodexConfig))

    def test_live_mode_requires_startup_only_model_configuration(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "HKM_MODEL_BASE_URL"):
            Settings.from_mapping({})
        mock = Settings.from_mapping({}, force_mock=True)
        self.assertTrue(mock.mock)

    def test_remote_http_and_non_loopback_bind_are_rejected(self) -> None:
        values = {
            "HKM_MODEL_BASE_URL": "http://example.com/v1",
            "HKM_MODEL_API_KEY": "secret",
            "HKM_MODEL_ID": "model",
        }
        with self.assertRaisesRegex(ConfigurationError, "HTTPS"):
            Settings.from_mapping(values)
        with self.assertRaisesRegex(ConfigurationError, "HKM_HOST"):
            Settings.from_mapping({**values, "HKM_MODEL_BASE_URL": "https://example.com/v1", "HKM_HOST": "0.0.0.0"})

    def test_secret_only_enters_runtime_environment(self) -> None:
        settings = self.live_settings()
        config = codex_config(settings)
        self.assertFalse(config_contains_secret(settings))
        self.assertEqual(config.env["HKM_MODEL_API_KEY"], "unit-test-secret")
        self.assertIn("features.shell_tool=false", config.config_overrides)
        self.assertIn("features.multi_agent=false", config.config_overrides)
        self.assertIn("tools.update_plan.enabled=true", config.config_overrides)
        self.assertIn("orchestrator.mcp.enabled=false", config.config_overrides)
        public = json.dumps(settings.public_summary())
        self.assertNotIn("unit-test-secret", public)
        self.assertNotIn("example.com", public)


if __name__ == "__main__":
    unittest.main()
