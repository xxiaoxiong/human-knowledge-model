import { createHash } from "node:crypto";

const REASONING_LEVELS = new Set(["minimal", "low", "medium", "high", "xhigh", "max"]);

function clean(value, max = 500) {
  return String(value || "").trim().slice(0, max);
}

function validateBaseUrl(value) {
  const url = new URL(value);
  const local = ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
  if (url.protocol !== "https:" && !(url.protocol === "http:" && local)) {
    throw new Error("模型地址必须使用 HTTPS；本机 localhost/127.0.0.1 可使用 HTTP。 ");
  }
  if (url.username || url.password) throw new Error("模型地址不能包含用户名或密码。");
  return url.toString().replace(/\/$/, "");
}

export function normalizeProvider(input = {}) {
  const kind = ["session", "openai", "custom", "ollama"].includes(input.kind) ? input.kind : "session";
  const provider = {
    kind,
    name: clean(input.name || (kind === "ollama" ? "Ollama" : kind === "custom" ? "Custom Responses Provider" : "OpenAI"), 80),
    model: clean(input.model, 160),
    baseUrl: clean(input.baseUrl, 500),
    apiKey: clean(input.apiKey, 1000),
    reasoningEffort: REASONING_LEVELS.has(input.reasoningEffort) ? input.reasoningEffort : "medium"
  };
  if (kind === "custom" || kind === "ollama") {
    provider.baseUrl = validateBaseUrl(provider.baseUrl || (kind === "ollama" ? "http://127.0.0.1:11434/v1" : ""));
    if (!provider.model) throw new Error("自定义模型需要填写模型 ID。");
  } else if (provider.baseUrl) {
    provider.baseUrl = validateBaseUrl(provider.baseUrl);
  }
  return provider;
}

export function providerFingerprint(provider) {
  return createHash("sha256")
    .update(JSON.stringify({ kind: provider.kind, name: provider.name, model: provider.model, baseUrl: provider.baseUrl, reasoningEffort: provider.reasoningEffort }))
    .digest("hex");
}

export function safeProviderSummary(provider) {
  return {
    kind: provider.kind,
    name: provider.name,
    model: provider.model || "Codex default",
    baseUrl: provider.baseUrl || null,
    reasoningEffort: provider.reasoningEffort,
    hasApiKey: Boolean(provider.apiKey)
  };
}

export function controlledEnvironment(apiKey = "") {
  const allowed = ["SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "PATH", "TEMP", "TMP", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "HOME", "SHELL", "LANG", "LC_ALL", "CODEX_HOME"];
  const env = {};
  const sourceEntries = Object.entries(process.env);
  for (const key of allowed) {
    const source = sourceEntries.find(([candidate]) => candidate.toUpperCase() === key);
    if (source?.[1]) env[key] = source[1];
  }
  if (apiKey) env.HKM_PROVIDER_API_KEY = apiKey;
  return env;
}
