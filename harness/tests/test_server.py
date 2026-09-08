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


class HostedServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.access_token = "hosted-test-access-token-32-characters"
        settings = Settings(
            host="127.0.0.1",
            port=0,
            mock=True,
            provider_name="",
            base_url="",
            api_key="",
            model_id="",
            reasoning_effort=None,
            deployment_mode="hosted",
            public_origin="https://hkm.example.com",
            access_token=cls.access_token,
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

    def post(self, path: str, body: dict, *, cookie: str = "", origin: str = "https://hkm.example.com"):
        headers = {"Content-Type": "application/json", "Origin": origin}
        if cookie:
            headers["Cookie"] = cookie
        return urllib.request.Request(
            self.base_url + path,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
        )

    def test_hosted_health_reports_locked_environment_only_agent(self) -> None:
        with urllib.request.urlopen(self.base_url + "/api/health", timeout=10) as response:
            health = json.loads(response.read().decode("utf-8"))
        self.assertTrue(health["auth"]["required"])
        self.assertFalse(health["auth"]["authenticated"])
        self.assertEqual(health["security"]["bind"], "public-https")
        self.assertEqual(health["security"]["config"], "environment-only")

    def test_hosted_agent_requires_origin_and_signed_cookie(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as denied_origin:
            urllib.request.urlopen(
                self.post("/api/auth/login", {"accessToken": self.access_token}, origin="https://evil.example"),
                timeout=10,
            )
        self.assertEqual(denied_origin.exception.code, 403)

        with self.assertRaises(urllib.error.HTTPError) as denied_analysis:
            urllib.request.urlopen(
                self.post("/api/analyze", {"query": "如何改善团队协作？"}),
                timeout=10,
            )
        self.assertEqual(denied_analysis.exception.code, 401)

        with urllib.request.urlopen(
            self.post("/api/auth/login", {"accessToken": self.access_token}),
            timeout=10,
        ) as response:
            cookie = response.headers["Set-Cookie"].split(";", 1)[0]
        self.assertTrue(cookie.startswith("hkm_session="))

        with urllib.request.urlopen(
            self.post("/api/analyze", {"query": "如何改善团队协作？"}, cookie=cookie),
            timeout=10,
        ) as response:
            events = [json.loads(line) for line in response.read().decode("utf-8").splitlines()]
        self.assertTrue(any(event["type"] == "final" for event in events))

    def test_access_token_is_never_reflected(self) -> None:
        supplied = "wrong-access-token"
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(
                self.post("/api/auth/login", {"accessToken": supplied}),
                timeout=10,
            )
        payload = raised.exception.read().decode("utf-8")
        self.assertEqual(raised.exception.code, 401)
        self.assertNotIn(supplied, payload)
        self.assertNotIn(self.access_token, payload)


if __name__ == "__main__":
    unittest.main()
