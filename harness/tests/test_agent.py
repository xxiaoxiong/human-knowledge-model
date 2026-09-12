from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from harness.agent import CodexAgent, _extract_response_text, _is_input_format_error
from harness.settings import Settings


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class AgentCompatibilityTests(unittest.TestCase):
    def settings(self) -> Settings:
        return Settings.from_mapping(
            {
                "HKM_MODEL_PROVIDER_NAME": "Partial Responses provider",
                "HKM_MODEL_BASE_URL": "https://example.com/v1",
                "HKM_MODEL_API_KEY": "unit-test-secret",
                "HKM_MODEL_ID": "test-model",
            }
        )

    def test_extracts_nested_responses_output_text(self) -> None:
        payload = {
            "output": [
                {"type": "reasoning", "content": [{"type": "reasoning_text", "text": "hidden"}]},
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": '{"version":"1"}'}],
                },
            ]
        }
        self.assertEqual(_extract_response_text(payload), '{"version":"1"}')

    def test_only_provider_input_400_enables_string_input_fallback(self) -> None:
        self.assertTrue(
            _is_input_format_error(
                RuntimeError("upstream_error 400: invalid input: failed to deserialize")
            )
        )
        self.assertFalse(_is_input_format_error(RuntimeError("upstream_error 401: invalid API key")))

    def test_direct_request_uses_string_input_and_keeps_secret_out_of_url(self) -> None:
        agent = CodexAgent(self.settings())
        response_payload = {
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": '{"version":"1"}'}],
                }
            ],
            "usage": {"input_tokens": 10, "output_tokens": 2},
        }
        captured = {}

        def fake_urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return _FakeResponse(response_payload)

        with patch("harness.agent.urllib.request.urlopen", side_effect=fake_urlopen):
            analysis, usage = agent._run_direct_response("test prompt")

        request = captured["request"]
        body = json.loads(request.data.decode("utf-8"))
        self.assertIsInstance(body["input"], str)
        self.assertIn("test prompt", body["input"])
        self.assertEqual(body["text"]["format"]["type"], "json_schema")
        self.assertNotIn("unit-test-secret", request.full_url)
        self.assertEqual(analysis["version"], "1")
        self.assertEqual(usage["output_tokens"], 2)
        self.assertEqual(captured["timeout"], 180)

    def test_codex_input_error_switches_future_turns_to_string_input(self) -> None:
        agent = CodexAgent(self.settings())
        result = ({"version": "1"}, None)
        with (
            patch.object(
                agent,
                "_run_codex_turn",
                side_effect=RuntimeError("upstream_error 400: invalid input deserialize"),
            ) as codex_turn,
            patch.object(agent, "_run_direct_response", return_value=result) as direct,
        ):
            self.assertEqual(agent.run_turn(object(), "first"), result)
            self.assertEqual(agent.run_turn(object(), "second"), result)

        codex_turn.assert_called_once()
        self.assertEqual(direct.call_count, 2)


if __name__ == "__main__":
    unittest.main()
