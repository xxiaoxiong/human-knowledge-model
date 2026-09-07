import http from "node:http";
import { randomUUID } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { buildHarnessPrompt } from "./lib/prompt.mjs";
import { createCodexThread, runCodexTurn } from "./lib/codex-runner.mjs";
import { createDeterministicAnalysis, groundAnalysis, loadGraph, REPO_ROOT, retrieveGraphContext } from "./lib/graph.mjs";
import { normalizeProvider, providerFingerprint, safeProviderSummary } from "./lib/provider.mjs";

const STATIC_ROOT = path.join(REPO_ROOT, "dist-site");
const MIME = new Map([
  [".html", "text/html; charset=utf-8"], [".js", "text/javascript; charset=utf-8"],
  [".css", "text/css; charset=utf-8"], [".json", "application/json; charset=utf-8"],
  [".png", "image/png"], [".xml", "application/xml; charset=utf-8"], [".txt", "text/plain; charset=utf-8"]
]);

function sendJson(response, status, value) {
  response.writeHead(status, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" });
  response.end(JSON.stringify(value));
}

async function readJson(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 1_000_000) throw new Error("请求内容过大。");
    chunks.push(chunk);
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
}

function streamEvent(response, event) {
  response.write(`${JSON.stringify(event)}\n`);
}

function publicRetrieval(retrieval) {
  const compact = (node) => ({ id: node.id, code: node.code, labels: node.labels, definition: node.definition });
  return {
    problemArchetypes: retrieval.topProblems.map(compact),
    domains: retrieval.selected.domains.map(compact),
    coreNodes: retrieval.selected.core_nodes.map(compact),
    thinkingModels: retrieval.selected.thinking_models.map(compact),
    universalModels: retrieval.selected.universal_models.map(compact),
    relationshipCount: retrieval.relations.length
  };
}

function codexProgress(event) {
  if (event.type === "thread.started") return { stage: "harness", message: "Codex Harness 已启动受控分析线程" };
  if (event.type === "turn.started") return { stage: "decompose", message: "正在展开问题边界与子问题" };
  if (event.type === "item.completed" && event.item?.type === "reasoning") return { stage: "reason", message: "正在比较解释、约束与候选路径" };
  if (event.type === "turn.completed") return { stage: "ground", message: "正在校验图谱节点、关系与行动门" };
  return null;
}

async function serveStatic(request, response) {
  const url = new URL(request.url, "http://127.0.0.1");
  const requested = decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname);
  const resolved = path.resolve(STATIC_ROOT, `.${requested}`);
  if (!resolved.startsWith(STATIC_ROOT + path.sep)) return sendJson(response, 403, { error: "Forbidden" });
  try {
    if (!(await stat(resolved)).isFile()) throw new Error("not a file");
    const content = await readFile(resolved);
    response.writeHead(200, {
      "content-type": MIME.get(path.extname(resolved).toLowerCase()) || "application/octet-stream",
      "cache-control": requested.endsWith("model.json") ? "no-cache" : "public, max-age=300",
      "content-security-policy": "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
      "x-content-type-options": "nosniff",
      "referrer-policy": "strict-origin-when-cross-origin"
    });
    response.end(content);
  } catch {
    sendJson(response, 404, { error: "Not found" });
  }
}

export async function createHarnessServer({ mock = false } = {}) {
  const graph = await loadGraph();
  const sessions = new Map();
  let activeRuns = 0;
  const server = http.createServer(async (request, response) => {
    try {
      const url = new URL(request.url, "http://127.0.0.1");
      if (request.method === "GET" && url.pathname === "/api/health") {
        return sendJson(response, 200, {
          ok: true,
          service: "hkm-codex-harness",
          mode: mock ? "mock" : "live",
          version: "0.9.0",
          security: { bind: "loopback", secretsPersisted: false, sandbox: "read-only", network: "disabled" }
        });
      }
      if (request.method === "POST" && url.pathname === "/api/session/reset") {
        const body = await readJson(request);
        if (body.sessionId) sessions.delete(String(body.sessionId));
        return sendJson(response, 200, { ok: true });
      }
      if (request.method === "POST" && url.pathname === "/api/analyze") {
        if (activeRuns >= 2) return sendJson(response, 429, { error: "当前已有两个分析在运行，请稍后重试。" });
        const body = await readJson(request);
        const query = String(body.query || "").trim();
        if (query.length < 4 || query.length > 4000) return sendJson(response, 400, { error: "问题长度需在 4–4000 个字符之间。" });
        const provider = normalizeProvider(body.provider || {});
        const conversation = Array.isArray(body.conversation)
          ? body.conversation.slice(-4).map((turn) => String(turn?.content || "").trim().slice(0, 2000)).filter(Boolean)
          : [];
        const retrieval = retrieveGraphContext(graph, [...conversation, query].join("\n"));
        const controller = new AbortController();
        response.on("close", () => {
          if (!response.writableEnded) controller.abort();
        });
        response.writeHead(200, {
          "content-type": "application/x-ndjson; charset=utf-8",
          "cache-control": "no-store",
          "x-content-type-options": "nosniff"
        });
        activeRuns += 1;
        let sessionId = String(body.sessionId || "");
        const fingerprint = providerFingerprint(provider);
        let session = sessions.get(sessionId);
        if (!session || session.fingerprint !== fingerprint) {
          sessionId = randomUUID();
          session = { fingerprint, thread: null, touchedAt: Date.now() };
          sessions.set(sessionId, session);
        }
        streamEvent(response, { type: "session", sessionId, provider: safeProviderSummary(provider) });
        streamEvent(response, { type: "progress", stage: "retrieve", message: "已从完整图谱检索问题原型、领域骨架与跨学科模型" });
        streamEvent(response, { type: "retrieval", data: publicRetrieval(retrieval) });
        try {
          let rawAnalysis;
          let usage = null;
          if (mock) {
            streamEvent(response, { type: "progress", stage: "decompose", message: "正在生成可复查的问题结构" });
            rawAnalysis = createDeterministicAnalysis(graph, retrieval, query);
          } else {
            if (!session.thread) session.thread = await createCodexThread(provider);
            const result = await runCodexTurn({
              thread: session.thread,
              prompt: buildHarnessPrompt({ query, retrieval, conversation }),
              signal: controller.signal,
              onEvent: (event) => {
                const progress = codexProgress(event);
                if (progress && !response.writableEnded) streamEvent(response, { type: "progress", ...progress });
              }
            });
            rawAnalysis = result.analysis;
            usage = result.usage;
          }
          const analysis = groundAnalysis(graph, retrieval, rawAnalysis, query);
          session.touchedAt = Date.now();
          streamEvent(response, { type: "final", sessionId, analysis, usage });
        } catch (error) {
          const message = error?.name === "AbortError" ? "分析已停止。" : String(error?.message || error).slice(0, 1000);
          streamEvent(response, { type: "error", error: message, recoverable: true });
        } finally {
          activeRuns -= 1;
          response.end();
        }
        return;
      }
      if (url.pathname.startsWith("/api/")) return sendJson(response, 404, { error: "Unknown API route" });
      return serveStatic(request, response);
    } catch (error) {
      if (!response.headersSent) sendJson(response, 400, { error: String(error?.message || error).slice(0, 1000) });
      else response.end();
    }
  });
  const cleanup = setInterval(() => {
    const cutoff = Date.now() - 2 * 60 * 60 * 1000;
    for (const [id, session] of sessions) if (session.touchedAt < cutoff) sessions.delete(id);
  }, 15 * 60 * 1000);
  cleanup.unref();
  return server;
}

export async function startServer({ host = process.env.HKM_HOST || "127.0.0.1", port = Number(process.env.HKM_PORT || 4317), mock = false } = {}) {
  if (!["127.0.0.1", "::1", "localhost"].includes(host)) throw new Error("安全限制：HKM Harness 只能绑定到本机回环地址。");
  const server = await createHarnessServer({ mock });
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, host, resolve);
  });
  const address = server.address();
  const actualPort = typeof address === "object" ? address.port : port;
  process.stdout.write(`HKM Codex Harness ready at http://${host}:${actualPort}\n`);
  return server;
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href;
if (isMain) {
  startServer({ mock: process.argv.includes("--mock") || process.env.HKM_HARNESS_MODE === "mock" }).catch((error) => {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  });
}
