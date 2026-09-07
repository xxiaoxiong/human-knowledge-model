import assert from "node:assert/strict";
import test from "node:test";
import { createDeterministicAnalysis, groundAnalysis, loadGraph, retrieveGraphContext } from "../lib/graph.mjs";

test("retrieval maps a career transition question into real HKM nodes", async () => {
  const graph = await loadGraph();
  const retrieval = retrieveGraphContext(graph, "我是否应该转行人工智能，同时控制收入中断风险？");
  assert.equal(retrieval.topProblems[0].code, "PT18");
  assert.ok(retrieval.selected.domains.some((node) => node.id === "hkm:domain:computing-information-ai"));
  assert.ok(retrieval.allowedIds.size > 10);
});

test("grounding removes hallucinated graph ids and preserves a complete result", async () => {
  const graph = await loadGraph();
  const query = "团队项目反复延期，怎样诊断并改善？";
  const retrieval = retrieveGraphContext(graph, query);
  const candidate = createDeterministicAnalysis(graph, retrieval, query);
  candidate.knowledge_map.domains.unshift({ node_id: "hkm:domain:not-real", relevance: "fake", role: "fake" });
  candidate.relationships.unshift({ source_id: "hkm:domain:not-real", type: "causes", target_id: "hkm:domain:also-fake", explanation: "fake" });
  const grounded = groundAnalysis(graph, retrieval, candidate, query);
  assert.ok(!grounded.knowledge_map.domains.some((item) => item.node_id.includes("not-real")));
  assert.ok(!grounded.relationships.some((item) => item.source_id.includes("not-real")));
  assert.ok(grounded.decomposition.length >= 5);
  assert.ok(grounded.solution_space.candidate_solutions.length >= 3);
});

test("explicit root-cause intent outranks incidental template vocabulary", async () => {
  const graph = await loadGraph();
  const retrieval = retrieveGraphContext(graph, "团队项目反复延期，成员互相甩锅，预算又不能增加。我们应该怎样定位根因并设计一个可执行的改善方案？");
  assert.equal(retrieval.topProblems[0].code, "PT02");
});
