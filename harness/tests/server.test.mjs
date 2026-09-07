import assert from "node:assert/strict";
import test from "node:test";
import { createHarnessServer } from "../server.mjs";

test("mock companion streams retrieval and a grounded final analysis", async (context) => {
  const server = await createHarnessServer({ mock: true });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  context.after(() => server.close());
  const { port } = server.address();
  const health = await fetch(`http://127.0.0.1:${port}/api/health`).then((response) => response.json());
  assert.equal(health.ok, true);
  assert.equal(health.security.sandbox, "read-only");

  const response = await fetch(`http://127.0.0.1:${port}/api/analyze`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ query: "如何判断一个新技术能否成功？", provider: { kind: "session" } })
  });
  assert.equal(response.status, 200);
  const events = (await response.text()).trim().split("\n").map(JSON.parse);
  assert.ok(events.some((event) => event.type === "retrieval"));
  const final = events.find((event) => event.type === "final");
  assert.ok(final.analysis.knowledge_map.domains.length > 0);
  assert.ok(final.analysis.solution_space.candidate_solutions.length >= 3);

  const followUpResponse = await fetch(`http://127.0.0.1:${port}/api/analyze`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      query: "如果只能先做一项零预算改动，应该验证哪个机制？",
      sessionId: final.sessionId,
      conversation: [{ role: "user", content: "团队项目反复延期，怎样定位根因并防止复发？" }],
      provider: { kind: "session" }
    })
  });
  const followUpEvents = (await followUpResponse.text()).trim().split("\n").map(JSON.parse);
  const followUpFinal = followUpEvents.find((event) => event.type === "final");
  assert.equal(followUpFinal.sessionId, final.sessionId);
  assert.match(followUpFinal.analysis.intent, /竞争解释|机制链|反事实/);
});
