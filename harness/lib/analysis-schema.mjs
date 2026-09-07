export const ANALYSIS_SCHEMA = {
  type: "object",
  additionalProperties: false,
  properties: {
    version: { type: "string" },
    problem_statement: { type: "string" },
    intent: { type: "string" },
    assumptions: { type: "array", items: { type: "string" } },
    scope: {
      type: "object",
      additionalProperties: false,
      properties: {
        objective: { type: "string" },
        system_boundary: { type: "string" },
        time_horizon: { type: "string" },
        stakeholders: { type: "array", items: { type: "string" } },
        constraints: { type: "array", items: { type: "string" } },
        success_criteria: { type: "array", items: { type: "string" } }
      },
      required: ["objective", "system_boundary", "time_horizon", "stakeholders", "constraints", "success_criteria"]
    },
    decomposition: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          id: { type: "string" },
          title: { type: "string" },
          question: { type: "string" },
          why_it_matters: { type: "string" },
          depends_on: { type: "array", items: { type: "string" } },
          knowledge_node_ids: { type: "array", items: { type: "string" } }
        },
        required: ["id", "title", "question", "why_it_matters", "depends_on", "knowledge_node_ids"]
      }
    },
    knowledge_map: {
      type: "object",
      additionalProperties: false,
      properties: {
        domains: { type: "array", items: { $ref: "#/$defs/knowledgeNode" } },
        core_nodes: { type: "array", items: { $ref: "#/$defs/knowledgeNode" } },
        thinking_models: { type: "array", items: { $ref: "#/$defs/knowledgeNode" } },
        universal_models: { type: "array", items: { $ref: "#/$defs/knowledgeNode" } }
      },
      required: ["domains", "core_nodes", "thinking_models", "universal_models"]
    },
    relationships: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          source_id: { type: "string" },
          type: { type: "string" },
          target_id: { type: "string" },
          explanation: { type: "string" }
        },
        required: ["source_id", "type", "target_id", "explanation"]
      }
    },
    solution_space: {
      type: "object",
      additionalProperties: false,
      properties: {
        candidate_solutions: {
          type: "array",
          items: {
            type: "object",
            additionalProperties: false,
            properties: {
              title: { type: "string" },
              mechanism: { type: "string" },
              prerequisites: { type: "array", items: { type: "string" } },
              benefits: { type: "array", items: { type: "string" } },
              risks: { type: "array", items: { type: "string" } },
              evidence_needed: { type: "array", items: { type: "string" } },
              reversibility: { type: "string" }
            },
            required: ["title", "mechanism", "prerequisites", "benefits", "risks", "evidence_needed", "reversibility"]
          }
        },
        comparison_criteria: { type: "array", items: { type: "string" } },
        provisional_strategy: { type: "string" }
      },
      required: ["candidate_solutions", "comparison_criteria", "provisional_strategy"]
    },
    evidence_plan: {
      type: "object",
      additionalProperties: false,
      properties: {
        knowns: { type: "array", items: { type: "string" } },
        unknowns: { type: "array", items: { type: "string" } },
        tests: { type: "array", items: { type: "string" } },
        escalation_conditions: { type: "array", items: { type: "string" } }
      },
      required: ["knowns", "unknowns", "tests", "escalation_conditions"]
    },
    next_actions: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          order: { type: "integer" },
          action: { type: "string" },
          output: { type: "string" },
          decision_gate: { type: "string" }
        },
        required: ["order", "action", "output", "decision_gate"]
      }
    },
    caveats: { type: "array", items: { type: "string" } }
  },
  required: [
    "version",
    "problem_statement",
    "intent",
    "assumptions",
    "scope",
    "decomposition",
    "knowledge_map",
    "relationships",
    "solution_space",
    "evidence_plan",
    "next_actions",
    "caveats"
  ],
  $defs: {
    knowledgeNode: {
      type: "object",
      additionalProperties: false,
      properties: {
        node_id: { type: "string" },
        relevance: { type: "string" },
        role: { type: "string" }
      },
      required: ["node_id", "relevance", "role"]
    }
  }
};

export function parseAnalysis(value) {
  if (value && typeof value === "object") return value;
  const text = String(value || "").trim();
  const unfenced = text.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  return JSON.parse(unfenced);
}
