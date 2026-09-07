from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request

from harness.server import create_server
from harness.settings import Settings


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        settings = Settings(
            host="127.0.0.1",
            port=0,
            mock=True,
            provider_name="",
            base_url="",
            api_key="",
            model_id="",
            reasoning_effort=None,
        )
        cls.server = create_server(settings)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request_json(self, path: str, body: dict | None = None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"} if data else {},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_health_is_safe_and_reports_environment_configuration(self) -> None:
        status, health = self.request_json("/api/health")
        self.assertEqual(status, 200)
        self.assertTrue(health["ok"])
        self.assertEqual(health["runtime"], "openai-codex")
        self.assertEqual(health["security"]["config"], "environment-only")
        self.assertFalse(health["security"]["browserSecrets"])

    def test_mock_analysis_streams_retrieval_and_grounded_result(self) -> None:
        request = urllib.request.Request(
            self.base_url + "/api/analyze",
            data=json.dumps({"query": "怎样判断一种新技术能否成功？"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            events = [json.loads(line) for line in response.read().decode("utf-8").splitlines()]
        self.assertTrue(any(event["type"] == "retrieval" for event in events))
        final = next(event for event in events if event["type"] == "final")
        self.assertTrue(final["analysis"]["knowledge_map"]["domains"])
        self.assertGreaterEqual(len(final["analysis"]["solution_space"]["candidate_solutions"]), 3)

    def test_browser_cannot_override_model_configuration(self) -> None:
        request = urllib.request.Request(
            self.base_url + "/api/analyze",
            data=json.dumps(
                {"query": "怎样改善团队协作？", "provider": {"apiKey": "browser-secret"}}
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(request, timeout=10)
        self.assertEqual(raised.exception.code, 400)
        payload = json.loads(raised.exception.read().decode("utf-8"))
        self.assertIn(".env", payload["error"])
        self.assertNotIn("browser-secret", json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
