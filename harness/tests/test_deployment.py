from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


class DeploymentTests(unittest.TestCase):
    def test_render_blueprint_keeps_secrets_out_of_source(self) -> None:
        blueprint = yaml.safe_load((ROOT / "render.yaml").read_text(encoding="utf-8"))
        service = blueprint["services"][0]
        self.assertEqual(service["type"], "web")
        self.assertEqual(service["runtime"], "docker")
        self.assertEqual(service["healthCheckPath"], "/api/health")
        variables = {item["key"]: item for item in service["envVars"]}
        for secret_name in ("HKM_MODEL_API_KEY", "HKM_ACCESS_TOKEN"):
            self.assertEqual(variables[secret_name], {"key": secret_name, "sync": False})
        self.assertEqual(variables["HKM_DEPLOYMENT_MODE"]["value"], "hosted")

    def test_container_excludes_env_and_runs_as_non_root(self) -> None:
        dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn(".env", dockerignore)
        self.assertIn("USER hkm", dockerfile)
        self.assertIn("python scripts/build_site.py", dockerfile)
        self.assertIn('["python", "-m", "harness.server"]', dockerfile)


if __name__ == "__main__":
    unittest.main()
