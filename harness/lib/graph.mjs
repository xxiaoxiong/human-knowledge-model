import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import YAML from "yaml";

const MODULE_DIR = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(MODULE_DIR, "..", "..");

const RELATION_FILES = [
  "relationships.yaml",
  "hierarchy-relationships.generated.yaml",
  "bridge-relationships.generated.yaml",
  "core-relationships.generated.yaml",
  "model-relationships.generated.yaml",
  "problem-relationships.generated.yaml",
  "learning-relationships.generated.yaml",
  "framework-relationships.generated.yaml"
];

const PROBLEM_HINTS = {
  PT01: ["现状", "测量", "指标", "数据", "measure", "metric"],
  PT02: ["为什么", "原因", "诊断", "故障", "失败", "根因", "定位根因", "延期", "复发", "diagnose", "cause", "failure", "root cause"],
  PT03: ["预测", "趋势", "预警", "未来", "forecast", "predict", "warning", "trend"],
  PT04: ["选择", "决定", "是否应该", "要不要", "不确定", "取舍", "decision", "choose", "uncertain"],
  PT05: ["分配", "资源", "预算", "排期", "瓶颈", "allocate", "resource", "budget", "bottleneck"],
  PT06: ["设计", "产品", "服务", "系统", "架构", "原型", "design", "product", "service", "prototype"],
  PT07: ["效果", "有效", "影响评估", "干预", "实验", "impact", "evaluate", "intervention"],
  PT08: ["治理", "监管", "规则", "制度", "政策设计", "governance", "regulation", "institution"],
  PT09: ["冲突", "谈判", "协商", "协调", "共识", "negotiate", "conflict", "consensus"],
  PT10: ["风险", "危机", "灾害", "恢复", "应急", "韧性", "risk", "crisis", "recovery"],
  PT11: ["战略", "组织变革", "转型", "竞争", "strategy", "organization", "transformation"],
  PT12: ["公司", "企业", "投资", "股票", "估值", "商业模式", "company", "invest", "valuation", "business"],
  PT13: ["新技术", "技术路线", "产业化", "成熟度", "technology", "technical", "adoption", "innovation"],
  PT14: ["社会政策", "福利", "教育政策", "住房政策", "公共服务", "social policy", "welfare"],
  PT15: ["健康", "医疗", "症状", "治疗", "药物", "疾病", "health", "medical", "treatment"],
  PT16: ["环境", "气候", "可持续", "减排", "能源转型", "environment", "climate", "sustainability"],
  PT17: ["学习", "教学", "技能", "课程", "训练", "教育", "learn", "teach", "skill", "education"],
  PT18: ["人生", "职业", "转行", "工作机会", "生活规划", "收入", "career", "life", "job", "income"],
  PT19: ["历史", "文化", "意义", "身份", "价值争议", "history", "culture", "meaning"],
  PT20: ["创作", "创新", "表达", "写作", "艺术", "创意", "create", "creative", "art", "write"]
};

async function readYaml(relativePath) {
  return YAML.parse(
    await readFile(path.join(REPO_ROOT, "08-data", relativePath), "utf8"),
    { maxAliasCount: 10_000 }
  );
}

function scalarText(value, output = []) {
  if (typeof value === "string" || typeof value === "number") output.push(String(value));
  else if (Array.isArray(value)) value.forEach((item) => scalarText(item, output));
  else if (value && typeof value === "object") Object.values(value).forEach((item) => scalarText(item, output));
  return output;
}

function normalize(value) {
  return String(value || "").normalize("NFKC").toLocaleLowerCase().replace(/\s+/g, " ").trim();
}

function queryTerms(query) {
  const normalized = normalize(query);
  const terms = new Set(normalized.match(/[a-z0-9][a-z0-9-]{1,}/g) || []);
  for (const chunk of normalized.match(/[\p{Script=Han}]{2,}/gu) || []) {
    terms.add(chunk);
    for (let width = 2; width <= Math.min(4, chunk.length); width += 1) {
      for (let index = 0; index <= chunk.length - width; index += 1) terms.add(chunk.slice(index, index + width));
    }
  }
  return [...terms].filter((term) => !["问题", "怎样", "如何", "什么", "一个", "should", "what", "how", "with"].includes(term));
}

function rankNodes(nodes, query, boosts = new Map()) {
  const terms = queryTerms(query);
  return nodes.map((node) => {
    const labelText = normalize(`${node.labels?.zh || ""} ${node.labels?.en || ""}`);
    const haystack = normalize(scalarText(node).join(" "));
    let score = boosts.get(node.id) || 0;
    for (const term of terms) {
      if (labelText.includes(term)) score += 8 + Math.min(term.length, 6);
      else if (haystack.includes(term)) score += 2 + Math.min(term.length, 5);
    }
    return { node, score };
  }).sort((a, b) => b.score - a.score || String(a.node.code).localeCompare(String(b.node.code)));
}

function compactNode(node) {
  return {
    id: node.id,
    code: node.code,
    labels: node.labels,
    primary_type: node.primary_type,
    definition: node.definition,
    core_idea: node.core_idea,
    core_structure: node.core_structure,
    boundary_notes: node.boundary_notes,
    primary_domain: node.primary_domain
  };
}

export async function loadGraph() {
  const [domains, subdomains, core, thinking, universal, problems, ...relationDocs] = await Promise.all([
    readYaml("domains.yaml"),
    readYaml("subdomains.yaml"),
    readYaml("core-nodes.yaml"),
    readYaml("thinking-models.yaml"),
    readYaml("universal-models.yaml"),
    readYaml("problem-templates.yaml"),
    ...RELATION_FILES.map(readYaml)
  ]);
  const groups = {
    domains: domains.domains,
    subdomains: subdomains.subdomains,
    core_nodes: core.core_nodes,
    thinking_models: thinking.thinking_models,
    universal_models: universal.universal_models,
    problem_templates: problems.problem_templates
  };
  const nodes = [domains.root, ...domains.superdomains, ...Object.values(groups).flat()];
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  return {
    ...groups,
    root: domains.root,
    superdomains: domains.superdomains,
    relationships: relationDocs.flatMap((doc) => doc.relationships || []),
    nodeById
  };
}

export function retrieveGraphContext(graph, query) {
  const normalized = normalize(query);
  const problemBoosts = new Map();
  for (const problem of graph.problem_templates) {
    const hints = PROBLEM_HINTS[problem.code] || [];
    // Explicit intent words should dominate incidental vocabulary overlap in the
    // much larger template bodies (for example, “根因” must beat generic data terms).
    const boost = hints.reduce((sum, hint) => sum + (normalized.includes(normalize(hint)) ? 32 : 0), 0);
    problemBoosts.set(problem.id, boost);
  }
  const problemRanks = rankNodes(graph.problem_templates, query, problemBoosts);
  const positiveProblems = problemRanks.filter((item) => item.score > 0);
  const topProblems = (positiveProblems.length ? positiveProblems : problemRanks).slice(0, 3).map((item) => item.node);

  const called = { domains: new Map(), core_nodes: new Map(), thinking_models: new Map(), universal_models: new Map() };
  topProblems.forEach((problem, problemIndex) => {
    const weight = 40 - problemIndex * 8;
    for (const [group, ids] of Object.entries(problem.knowledge_calls || {})) {
      if (!called[group]) continue;
      (ids || []).forEach((id) => called[group].set(id, Math.max(called[group].get(id) || 0, weight)));
    }
  });

  const select = (group, limit) => rankNodes(graph[group], query, called[group])
    .filter((item) => item.score > 0)
    .slice(0, limit)
    .map((item) => item.node);
  const selected = {
    domains: select("domains", 8),
    core_nodes: select("core_nodes", 12),
    thinking_models: select("thinking_models", 8),
    universal_models: select("universal_models", 6)
  };
  const allowedIds = new Set([
    ...topProblems.map((node) => node.id),
    ...Object.values(selected).flat().map((node) => node.id)
  ]);
  const relations = graph.relationships
    .filter((relation) => allowedIds.has(relation.source) && allowedIds.has(relation.target))
    .sort((a, b) => Number(b.source.startsWith("hkm:problem-template")) - Number(a.source.startsWith("hkm:problem-template")))
    .slice(0, 30);

  return {
    query,
    topProblems,
    selected,
    relations,
    allowedIds,
    promptContext: {
      problem_archetypes: topProblems.map((problem) => ({
        ...compactNode(problem),
        problem_family: problem.problem_family,
        primary_aim: problem.primary_aim,
        trigger_questions: problem.trigger_questions,
        success_criteria: problem.success_criteria,
        scoping_dimensions: problem.scoping_dimensions,
        evidence_requirements: problem.evidence_requirements,
        workflow: problem.workflow,
        failure_modes: problem.failure_modes,
        escalation_conditions: problem.escalation_conditions,
        knowledge_calls: problem.knowledge_calls
      })),
      knowledge_nodes: Object.fromEntries(Object.entries(selected).map(([key, nodes]) => [key, nodes.map(compactNode)])),
      graph_relationships: relations.map((relation) => ({
        source_id: relation.source,
        type: relation.type,
        target_id: relation.target,
        explanation: relation.scope
      }))
    }
  };
}

function list(value, fallback = []) {
  return Array.isArray(value) && value.length ? value : fallback;
}

function nodeEntry(node, role) {
  return { node_id: node.id, relevance: node.definition || role, role };
}

export function createDeterministicAnalysis(graph, retrieval, query) {
  const problem = retrieval.topProblems[0];
  const scope = problem.scoping_dimensions || {};
  const workflow = list(problem.workflow);
  const firstThinking = retrieval.selected.thinking_models[0];
  const firstUniversal = retrieval.selected.universal_models[0];
  const evidence = list(problem.evidence_requirements, ["收集能区分不同解释的证据"]);
  return {
    version: "hkm-analysis/1.0",
    problem_statement: query,
    intent: problem.definition || "把现实问题转换为可检验、可比较、可行动的结构。",
    assumptions: ["当前输入仍可能缺少关键情境，以下结构是待验证的工作假设。", "满意解取决于价值权重、硬约束与证据质量，不能预先宣称穷尽。"],
    scope: {
      objective: list(problem.success_criteria, ["形成可检查的判断与行动路径"])[0],
      system_boundary: list(scope.objects, ["问题对象"] ).join("、"),
      time_horizon: list(scope.timescales, ["短期行动与长期影响"]).join("、"),
      stakeholders: list(scope.actors, ["决策者与受影响者"]),
      constraints: list(scope.constraints, ["信息、资源与时间约束"]),
      success_criteria: list(problem.success_criteria, ["结论可被证据更新"])
    },
    decomposition: workflow.map((step, index) => ({
      id: `Q${index + 1}`,
      title: step.action,
      question: `${step.action}时，需要回答哪些可检验的子问题？`,
      why_it_matters: step.gate,
      depends_on: index ? [`Q${index}`] : [],
      knowledge_node_ids: [
        retrieval.selected.core_nodes[index % Math.max(retrieval.selected.core_nodes.length, 1)]?.id,
        retrieval.selected.thinking_models[index % Math.max(retrieval.selected.thinking_models.length, 1)]?.id
      ].filter(Boolean)
    })),
    knowledge_map: {
      domains: retrieval.selected.domains.map((node) => nodeEntry(node, "提供问题所属的学科视角与证据传统")),
      core_nodes: retrieval.selected.core_nodes.map((node) => nodeEntry(node, "提供可操作的领域机制与方法")),
      thinking_models: retrieval.selected.thinking_models.map((node) => nodeEntry(node, "用于检查推理、偏差与权衡")),
      universal_models: retrieval.selected.universal_models.map((node) => nodeEntry(node, "用于识别跨领域重复出现的系统结构"))
    },
    relationships: retrieval.relations.slice(0, 18).map((relation) => ({
      source_id: relation.source,
      type: relation.type,
      target_id: relation.target,
      explanation: relation.scope
    })),
    solution_space: {
      candidate_solutions: [
        {
          title: "低成本基线与信息增益方案",
          mechanism: `先按${workflow[0]?.action || "问题定义"}建立基线，再优先消除会改变方案排序的未知。`,
          prerequisites: ["明确成功标准", "可取得最低限度的基线证据"],
          benefits: ["可逆", "降低过早承诺", "暴露关键未知"],
          risks: ["短期看起来进展较慢", "可能低估结构性约束"],
          evidence_needed: evidence.slice(0, 2),
          reversibility: "高：可在新证据出现后快速调整"
        },
        {
          title: "受控试点与反馈学习方案",
          mechanism: `用${firstThinking?.labels?.zh || "实验迭代"}设计小规模试点，并以${firstUniversal?.labels?.zh || "反馈结构"}持续更新。`,
          prerequisites: ["能隔离试点范围", "定义停止、扩大和回滚阈值"],
          benefits: ["把争论转为可观察反馈", "兼顾行动与学习"],
          risks: ["试点情境可能不代表全面实施", "反馈指标可能被误设"],
          evidence_needed: evidence.slice(0, 3),
          reversibility: "中高：在明确回滚条件下逐步扩大"
        },
        {
          title: "结构性重构方案",
          mechanism: "针对瓶颈、激励、接口或制度约束改变系统结构，而不是只优化表面症状。",
          prerequisites: ["确认根因层级", "获得相关主体授权与资源"],
          benefits: ["可能解决反复出现的问题", "长期收益更高"],
          risks: ["成本与不可逆性更高", "二阶效应和主体反应更强"],
          evidence_needed: evidence,
          reversibility: "较低：应先通过情景、原型或阶段门降低承诺风险"
        }
      ],
      comparison_criteria: ["目标达成度", "证据可信度", "成本与机会成本", "风险与最坏情形", "可逆性", "公平与外部性", "长期适应性"],
      provisional_strategy: "先运行低成本基线与受控试点；只有在关键机制得到区分性证据支持后，才升级为结构性重构。"
    },
    evidence_plan: {
      knowns: ["用户已明确提出的问题陈述"],
      unknowns: list(problem.trigger_questions, ["哪些未知会改变方案排序？"]),
      tests: evidence,
      escalation_conditions: list(problem.escalation_conditions, ["当风险、不可逆性或专业责任超过当前能力边界时升级"])
    },
    next_actions: workflow.map((step, index) => ({ order: index + 1, action: step.action, output: step.output, decision_gate: step.gate })),
    caveats: [problem.boundary_notes || "该框架提供求解结构，不替代特定领域的专业判断。", "图谱用于扩大和组织问题空间；最终结论仍需现实证据、价值选择与责任主体确认。"]
  };
}

export function groundAnalysis(graph, retrieval, candidate, query) {
  const base = createDeterministicAnalysis(graph, retrieval, query);
  const value = candidate && typeof candidate === "object" ? candidate : {};
  const allowed = retrieval.allowedIds;
  const validString = (item, fallback, max = 1200) => typeof item === "string" && item.trim() ? item.trim().slice(0, max) : fallback;
  const strings = (items, fallback, limit = 12) => Array.isArray(items)
    ? items.filter((item) => typeof item === "string" && item.trim()).slice(0, limit).map((item) => item.trim().slice(0, 600))
    : fallback;
  const knowledge = {};
  for (const key of ["domains", "core_nodes", "thinking_models", "universal_models"]) {
    const incoming = Array.isArray(value.knowledge_map?.[key]) ? value.knowledge_map[key] : [];
    const grounded = incoming.filter((item) => allowed.has(item?.node_id)).slice(0, 12).map((item) => ({
      node_id: item.node_id,
      relevance: validString(item.relevance, graph.nodeById.get(item.node_id)?.definition || "与问题相关"),
      role: validString(item.role, "图谱调用节点", 240)
    }));
    knowledge[key] = grounded.length ? grounded : base.knowledge_map[key];
  }
  const graphRelationByKey = new Map(graph.relationships.map((relation) => [`${relation.source}|${relation.type}|${relation.target}`, relation]));
  const incomingRelations = Array.isArray(value.relationships) ? value.relationships : [];
  const relationships = incomingRelations.flatMap((item) => {
    if (!allowed.has(item?.source_id) || !allowed.has(item?.target_id)) return [];
    const relation = graphRelationByKey.get(`${item.source_id}|${item.type}|${item.target_id}`);
    if (!relation) return [];
    return [{ source_id: relation.source, type: relation.type, target_id: relation.target, explanation: validString(item.explanation, relation.scope) }];
  }).slice(0, 24);
  const normalizedSolutions = Array.isArray(value.solution_space?.candidate_solutions)
    ? value.solution_space.candidate_solutions.slice(0, 8).map((item, index) => ({
        title: validString(item?.title, base.solution_space.candidate_solutions[index % 3].title, 180),
        mechanism: validString(item?.mechanism, base.solution_space.candidate_solutions[index % 3].mechanism),
        prerequisites: strings(item?.prerequisites, [], 8),
        benefits: strings(item?.benefits, [], 8),
        risks: strings(item?.risks, [], 8),
        evidence_needed: strings(item?.evidence_needed, [], 8),
        reversibility: validString(item?.reversibility, "需要进一步评估", 240)
      }))
    : [];
  const scope = value.scope || {};
  return {
    version: "hkm-analysis/1.0",
    problem_statement: validString(value.problem_statement, query),
    intent: validString(value.intent, base.intent),
    assumptions: strings(value.assumptions, base.assumptions),
    scope: {
      objective: validString(scope.objective, base.scope.objective),
      system_boundary: validString(scope.system_boundary, base.scope.system_boundary),
      time_horizon: validString(scope.time_horizon, base.scope.time_horizon),
      stakeholders: strings(scope.stakeholders, base.scope.stakeholders),
      constraints: strings(scope.constraints, base.scope.constraints),
      success_criteria: strings(scope.success_criteria, base.scope.success_criteria)
    },
    decomposition: Array.isArray(value.decomposition) && value.decomposition.length
      ? value.decomposition.slice(0, 12).map((item, index) => ({
          id: `Q${index + 1}`,
          title: validString(item?.title, `子问题 ${index + 1}`, 180),
          question: validString(item?.question, "需要进一步澄清什么？"),
          why_it_matters: validString(item?.why_it_matters, "它可能改变方案排序。"),
          depends_on: strings(item?.depends_on, [], 8).filter((id) => /^Q\d+$/.test(id)),
          knowledge_node_ids: strings(item?.knowledge_node_ids, [], 8).filter((id) => allowed.has(id))
        }))
      : base.decomposition,
    knowledge_map: knowledge,
    relationships: relationships.length ? relationships : base.relationships,
    solution_space: {
      candidate_solutions: normalizedSolutions.length ? normalizedSolutions : base.solution_space.candidate_solutions,
      comparison_criteria: strings(value.solution_space?.comparison_criteria, base.solution_space.comparison_criteria),
      provisional_strategy: validString(value.solution_space?.provisional_strategy, base.solution_space.provisional_strategy)
    },
    evidence_plan: {
      knowns: strings(value.evidence_plan?.knowns, base.evidence_plan.knowns),
      unknowns: strings(value.evidence_plan?.unknowns, base.evidence_plan.unknowns),
      tests: strings(value.evidence_plan?.tests, base.evidence_plan.tests),
      escalation_conditions: strings(value.evidence_plan?.escalation_conditions, base.evidence_plan.escalation_conditions)
    },
    next_actions: Array.isArray(value.next_actions) && value.next_actions.length
      ? value.next_actions.slice(0, 10).map((item, index) => ({
          order: index + 1,
          action: validString(item?.action, `执行步骤 ${index + 1}`),
          output: validString(item?.output, "可检查的阶段产物"),
          decision_gate: validString(item?.decision_gate, "通过后再进入下一步")
        }))
      : base.next_actions,
    caveats: strings(value.caveats, base.caveats)
  };
}
