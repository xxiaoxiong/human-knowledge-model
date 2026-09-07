import { ANALYSIS_SCHEMA, parseAnalysis } from "./analysis-schema.mjs";
import { controlledEnvironment } from "./provider.mjs";
import { REPO_ROOT } from "./graph.mjs";
import path from "node:path";

function createOptions(provider) {
  const env = controlledEnvironment(provider.kind === "custom" ? provider.apiKey : "");
  if (provider.kind === "session") return { env, config: { mcp_servers: {} } };
  if (provider.kind === "openai") {
    return { env, apiKey: provider.apiKey || undefined, baseUrl: provider.baseUrl || undefined, config: { mcp_servers: {} } };
  }
  const custom = {
    name: provider.name,
    base_url: provider.baseUrl,
    wire_api: "responses"
  };
  if (provider.apiKey) custom.env_key = "HKM_PROVIDER_API_KEY";
  return {
    env,
    config: {
      model_provider: "hkm_user",
      model_providers: { hkm_user: custom },
      mcp_servers: {}
    }
  };
}

export async function createCodexThread(provider) {
  const { Codex } = await import("@openai/codex-sdk");
  const codex = new Codex(createOptions(provider));
  return codex.startThread({
    model: provider.model || undefined,
    sandboxMode: "read-only",
    workingDirectory: path.join(REPO_ROOT, "harness", "workspace"),
    modelReasoningEffort: provider.reasoningEffort,
    networkAccessEnabled: false,
    webSearchMode: "disabled",
    approvalPolicy: "never"
  });
}

export async function runCodexTurn({ thread, prompt, signal, onEvent }) {
  const { events } = await thread.runStreamed(prompt, { outputSchema: ANALYSIS_SCHEMA, signal });
  let finalResponse = "";
  let usage = null;
  for await (const event of events) {
    if (event.type === "item.completed" && event.item?.type === "agent_message") finalResponse = event.item.text;
    if (event.type === "turn.completed") usage = event.usage;
    onEvent?.(event);
  }
  if (!finalResponse) throw new Error("模型没有返回结构化分析结果。");
  return { analysis: parseAnalysis(finalResponse), usage, threadId: thread.id };
}
