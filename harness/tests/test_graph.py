from __future__ import annotations

import unittest

from harness.graph import (
    create_deterministic_analysis,
    ground_analysis,
    load_graph,
    retrieve_graph_context,
)


class GraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = load_graph()

    def test_career_question_maps_to_real_nodes(self) -> None:
        retrieval = retrieve_graph_context(
            self.graph,
            "我是否应该转行人工智能，同时控制收入中断风险？",
        )
        self.assertEqual(retrieval["top_problems"][0]["code"], "PT18")
        self.assertTrue(
            any(
                node["id"] == "hkm:domain:computing-information-ai"
                for node in retrieval["selected"]["domains"]
            )
        )
        self.assertGreater(len(retrieval["allowed_ids"]), 10)

    def test_grounding_removes_hallucinated_graph_ids(self) -> None:
        query = "团队项目反复延期，怎样诊断并改善？"
        retrieval = retrieve_graph_context(self.graph, query)
        candidate = create_deterministic_analysis(self.graph, retrieval, query)
        candidate["knowledge_map"]["domains"].insert(
            0,
            {"node_id": "hkm:domain:not-real", "relevance": "fake", "role": "fake"},
        )
        candidate["relationships"].insert(
            0,
            {
                "source_id": "hkm:domain:not-real",
                "type": "causes",
                "target_id": "hkm:domain:also-fake",
                "explanation": "fake",
            },
        )
        grounded = ground_analysis(self.graph, retrieval, candidate, query)
        self.assertFalse(
            any("not-real" in item["node_id"] for item in grounded["knowledge_map"]["domains"])
        )
        self.assertFalse(
            any("not-real" in item["source_id"] for item in grounded["relationships"])
        )
        self.assertGreaterEqual(len(grounded["decomposition"]), 5)
        self.assertGreaterEqual(len(grounded["solution_space"]["candidate_solutions"]), 3)

    def test_root_cause_intent_outranks_incidental_words(self) -> None:
        retrieval = retrieve_graph_context(
            self.graph,
            "团队项目反复延期，成员互相甩锅，预算不能增加。怎样定位根因并设计改善方案？",
        )
        self.assertEqual(retrieval["top_problems"][0]["code"], "PT02")


if __name__ == "__main__":
    unittest.main()
