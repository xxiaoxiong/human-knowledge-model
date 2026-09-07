import assert from "node:assert/strict";
import test from "node:test";
import { createCodexThread } from "../lib/codex-runner.mjs";
import { controlledEnvironment, normalizeProvider, providerFingerprint, safeProviderSummary } from "../lib/provider.mjs";

test("provider validation permits local HTTP but rejects remote insecure URLs", () => {
  const local = normalizeProvider({ kind: "ollama", model: "qwen3", baseUrl: "http://127.0.0.1:11434/v1" });
  assert.equal(local.baseUrl, "http://127.0.0.1:11434/v1");
  assert.throws(
    () => normalizeProvider({ kind: "custom", model: "m", baseUrl: "http://example.com/v1" }),
    /HTTPS/
  );
});

test("API keys are omitted from summaries, fingerprints, and unrelated environment", () => {
  const provider = normalizeProvider({ kind: "custom", model: "m", baseUrl: "https://example.com/v1", apiKey: "top-secret" });
  assert.equal(safeProviderSummary(provider).hasApiKey, true);
  assert.ok(!JSON.stringify(safeProviderSummary(provider)).includes("top-secret"));
  assert.ok(!providerFingerprint(provider).includes("top-secret"));
  assert.equal(controlledEnvironment().HKM_PROVIDER_API_KEY, undefined);
  assert.equal(controlledEnvironment(provider.apiKey).HKM_PROVIDER_API_KEY, "top-secret");
  const environmentKeys = Object.keys(controlledEnvironment()).map((key) => key.toUpperCase());
  assert.equal(new Set(environmentKeys).size, environmentKeys.length);
});

test("official Codex SDK can construct an isolated read-only thread", async () => {
  const provider = normalizeProvider({ kind: "session", reasoningEffort: "medium" });
  const thread = await createCodexThread(provider);
  assert.equal(typeof thread.runStreamed, "function");
});
