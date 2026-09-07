"""Load, retrieve, and deterministically ground the Human Knowledge Model graph."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "08-data"
RELATION_FILES = (
    "relationships.yaml",
    "hierarchy-relationships.generated.yaml",
    "bridge-relationships.generated.yaml",
    "core-relationships.generated.yaml",
    "model-relationships.generated.yaml",
    "problem-relationships.generated.yaml",
    "learning-relationships.generated.yaml",
    "framework-relationships.generated.yaml",
)

PROBLEM_HINTS = {
    "PT01": ("现状", "测量", "指标", "数据", "measure", "metric"),
    "PT02": ("为什么", "原因", "诊断", "故障", "失败", "根因", "定位根因", "延期", "复发", "diagnose", "cause", "failure", "root cause"),
    "PT03": ("预测", "趋势", "预警", "未来", "forecast", "predict", "warning", "trend"),
    "PT04": ("选择", "决定", "是否应该", "要不要", "不确定", "取舍", "decision", "choose", "uncertain"),
    "PT05": ("分配", "资源", "预算", "排期", "瓶颈", "allocate", "resource", "budget", "bottleneck"),
    "PT06": ("设计", "产品", "服务", "系统", "架构", "原型", "design", "product", "service", "prototype"),
    "PT07": ("效果", "有效", "影响评估", "干预", "实验", "impact", "evaluate", "intervention"),
    "PT08": ("治理", "监管", "规则", "制度", "政策设计", "governance", "regulation", "institution"),
    "PT09": ("冲突", "谈判", "协商", "协调", "共识", "negotiate", "conflict", "consensus"),
    "PT10": ("风险", "危机", "灾害", "恢复", "应急", "韧性", "risk", "crisis", "recovery"),
    "PT11": ("战略", "组织变革", "转型", "竞争", "strategy", "organization", "transformation"),
    "PT12": ("公司", "企业", "投资", "股票", "估值", "商业模式", "company", "invest", "valuation", "business"),
    "PT13": ("新技术", "技术路线", "产业化", "成熟度", "technology", "technical", "adoption", "innovation"),
    "PT14": ("社会政策", "福利", "教育政策", "住房政策", "公共服务", "social policy", "welfare"),
    "PT15": ("健康", "医疗", "症状", "治疗", "药物", "疾病", "health", "medical", "treatment"),
    "PT16": ("环境", "气候", "可持续", "减排", "能源转型", "environment", "climate", "sustainability"),
    "PT17": ("学习", "教学", "技能", "课程", "训练", "教育", "learn", "teach", "skill", "education"),
    "PT18": ("人生", "职业", "转行", "工作机会", "生活规划", "收入", "career", "life", "job", "income"),
    "PT19": ("历史", "文化", "意义", "身份", "价值争议", "history", "culture", "meaning"),
    "PT20": ("创作", "创新", "表达", "写作", "艺术", "创意", "create", "creative", "art", "write"),
}

STOP_TERMS = {"问题", "怎样", "如何", "什么", "一个", "should", "what", "how", "with"}
KNOWLEDGE_GROUPS = ("domains", "core_nodes", "thinking_models", "universal_models")


@dataclass(slots=True)
class Graph:
    root: dict[str, Any]
    superdomains: list[dict[str, Any]]
    domains: list[dict[str, Any]]
    subdomains: list[dict[str, Any]]
    core_nodes: list[dict[str, Any]]
    thinking_models: list[dict[str, Any]]
    universal_models: list[dict[str, Any]]
    problem_templates: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    node_by_id: dict[str, dict[str, Any]]


def _read_yaml(name: str) -> dict[str, Any]:
    with (DATA_DIR / name).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_graph() -> Graph:
    domains = _read_yaml("domains.yaml")
    subdomains = _read_yaml("subdomains.yaml")
    core = _read_yaml("core-nodes.yaml")
    thinking = _read_yaml("thinking-models.yaml")
    universal = _read_yaml("universal-models.yaml")
    problems = _read_yaml("problem-templates.yaml")
    relationships = [
        relation
        for name in RELATION_FILES
        for relation in (_read_yaml(name).get("relationships") or [])
    ]
    groups = {
        "domains": domains["domains"],
        "subdomains": subdomains["subdomains"],
        "core_nodes": core["core_nodes"],
        "thinking_models": thinking["thinking_models"],
        "universal_models": universal["universal_models"],
        "problem_templates": problems["problem_templates"],
    }
    nodes = [domains["root"], *domains["superdomains"]]
    for collection in groups.values():
        nodes.extend(collection)
    return Graph(
        root=domains["root"],
        superdomains=domains["superdomains"],
        relationships=relationships,
        node_by_id={node["id"]: node for node in nodes},
        **groups,
    )


def _scalar_text(value: Any) -> Iterable[str]:
    if isinstance(value, (str, int, float)):
        yield str(value)
    elif isinstance(value, list):
        for item in value:
            yield from _scalar_text(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _scalar_text(item)


def _normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).lower()
    return re.sub(r"\s+", " ", text).strip()


def _query_terms(query: str) -> list[str]:
    normalized = _normalize(query)
    terms = set(re.findall(r"[a-z0-9][a-z0-9-]{1,}", normalized))
    for chunk in re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]{2,}", normalized):
        terms.add(chunk)
        for width in range(2, min(4, len(chunk)) + 1):
            for index in range(len(chunk) - width + 1):
                terms.add(chunk[index : index + width])
    return [term for term in terms if term not in STOP_TERMS]


def _rank_nodes(
    nodes: list[dict[str, Any]],
    query: str,
    boosts: dict[str, int] | None = None,
) -> list[tuple[dict[str, Any], int]]:
    terms = _query_terms(query)
    boosts = boosts or {}
    ranked: list[tuple[dict[str, Any], int]] = []
    for node in nodes:
        labels = node.get("labels") or {}
        label_text = _normalize(f"{labels.get('zh', '')} {labels.get('en', '')}")
        haystack = _normalize(" ".join(_scalar_text(node)))
        score = boosts.get(node["id"], 0)
        for term in terms:
            if term in label_text:
                score += 8 + min(len(term), 6)
            elif term in haystack:
                score += 2 + min(len(term), 5)
        ranked.append((node, score))
    return sorted(ranked, key=lambda item: (-item[1], str(item[0].get("code", ""))))


def _compact_node(node: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "id",
        "code",
        "labels",
        "primary_type",
        "definition",
        "core_idea",
        "core_structure",
        "boundary_notes",
        "primary_domain",
    )
    return {field: node.get(field) for field in fields}


def retrieve_graph_context(graph: Graph, query: str) -> dict[str, Any]:
    normalized = _normalize(query)
    problem_boosts = {
        problem["id"]: sum(
            32 for hint in PROBLEM_HINTS.get(problem.get("code", ""), ()) if _normalize(hint) in normalized
        )
        for problem in graph.problem_templates
    }
    problem_ranks = _rank_nodes(graph.problem_templates, query, problem_boosts)
    positive = [item for item in problem_ranks if item[1] > 0]
    top_problems = [node for node, _score in (positive or problem_ranks)[:3]]

    called: dict[str, dict[str, int]] = {name: {} for name in KNOWLEDGE_GROUPS}
    for problem_index, problem in enumerate(top_problems):
        weight = 40 - problem_index * 8
        for group, ids in (problem.get("knowledge_calls") or {}).items():
            if group not in called:
                continue
            for node_id in ids or []:
                called[group][node_id] = max(called[group].get(node_id, 0), weight)

    def select(group: str, limit: int) -> list[dict[str, Any]]:
        ranked = _rank_nodes(getattr(graph, group), query, called[group])
        return [node for node, score in ranked if score > 0][:limit]

    selected = {
        "domains": select("domains", 8),
        "core_nodes": select("core_nodes", 12),
        "thinking_models": select("thinking_models", 8),
        "universal_models": select("universal_models", 6),
    }
    allowed_ids = {problem["id"] for problem in top_problems}
    allowed_ids.update(node["id"] for nodes in selected.values() for node in nodes)
    relations = [
        relation
        for relation in graph.relationships
        if relation.get("source") in allowed_ids and relation.get("target") in allowed_ids
    ]
    relations.sort(key=lambda relation: not str(relation.get("source", "")).startswith("hkm:problem-template"))
    relations = relations[:30]

    prompt_problems = []
    for problem in top_problems:
        prompt_problems.append(
            {
                **_compact_node(problem),
                **{
                    key: problem.get(key)
                    for key in (
                        "problem_family",
                        "primary_aim",
                        "trigger_questions",
                        "success_criteria",
                        "scoping_dimensions",
                        "evidence_requirements",
                        "workflow",
                        "failure_modes",
                        "escalation_conditions",
                        "knowledge_calls",
                    )
                },
            }
        )
    return {
        "query": query,
        "top_problems": top_problems,
        "selected": selected,
        "relations": relations,
        "allowed_ids": allowed_ids,
        "prompt_context": {
            "problem_archetypes": prompt_problems,
            "knowledge_nodes": {
                key: [_compact_node(node) for node in nodes] for key, nodes in selected.items()
            },
            "graph_relationships": [
                {
                    "source_id": relation["source"],
                    "type": relation["type"],
                    "target_id": relation["target"],
                    "explanation": relation.get("scope", ""),
                }
                for relation in relations
            ],
        },
    }


def public_retrieval(retrieval: dict[str, Any]) -> dict[str, Any]:
    def compact(node: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": node["id"],
            "code": node.get("code"),
            "labels": node.get("labels"),
            "definition": node.get("definition"),
        }

    selected = retrieval["selected"]
    return {
        "problemArchetypes": [compact(node) for node in retrieval["top_problems"]],
        "domains": [compact(node) for node in selected["domains"]],
        "coreNodes": [compact(node) for node in selected["core_nodes"]],
        "thinkingModels": [compact(node) for node in selected["thinking_models"]],
        "universalModels": [compact(node) for node in selected["universal_models"]],
        "relationshipCount": len(retrieval["relations"]),
    }


def _nonempty_list(value: Any, fallback: list[Any] | None = None) -> list[Any]:
    return value if isinstance(value, list) and value else (fallback or [])


def _node_entry(node: dict[str, Any], role: str) -> dict[str, str]:
    return {"node_id": node["id"], "relevance": node.get("definition") or role, "role": role}


def create_deterministic_analysis(
    graph: Graph,
    retrieval: dict[str, Any],
    query: str,
) -> dict[str, Any]:
    problem = retrieval["top_problems"][0]
    scope = problem.get("scoping_dimensions") or {}
    workflow = _nonempty_list(problem.get("workflow"))
    selected = retrieval["selected"]
    thinking = selected["thinking_models"][0] if selected["thinking_models"] else None
    universal = selected["universal_models"][0] if selected["universal_models"] else None
    evidence = _nonempty_list(problem.get("evidence_requirements"), ["收集能区分不同解释的证据"])

    decomposition = []
    for index, step in enumerate(workflow):
        node_ids = []
        if selected["core_nodes"]:
            node_ids.append(selected["core_nodes"][index % len(selected["core_nodes"])]["id"])
        if selected["thinking_models"]:
            node_ids.append(selected["thinking_models"][index % len(selected["thinking_models"])]["id"])
        decomposition.append(
            {
                "id": f"Q{index + 1}",
                "title": step["action"],
                "question": f"{step['action']}时，需要回答哪些可检验的子问题？",
                "why_it_matters": step["gate"],
                "depends_on": [f"Q{index}"] if index else [],
                "knowledge_node_ids": node_ids,
            }
        )

    thinking_label = ((thinking or {}).get("labels") or {}).get("zh", "实验迭代")
    universal_label = ((universal or {}).get("labels") or {}).get("zh", "反馈结构")
    return {
        "version": "hkm-analysis/1.0",
        "problem_statement": query,
        "intent": problem.get("definition") or "把现实问题转换为可检验、可比较、可行动的结构。",
        "assumptions": [
            "当前输入仍可能缺少关键情境，以下结构是待验证的工作假设。",
            "满意解取决于价值权重、硬约束与证据质量，不能预先宣称穷尽。",
        ],
        "scope": {
            "objective": _nonempty_list(problem.get("success_criteria"), ["形成可检查的判断与行动路径"])[0],
            "system_boundary": "、".join(_nonempty_list(scope.get("objects"), ["问题对象"])),
            "time_horizon": "、".join(_nonempty_list(scope.get("timescales"), ["短期行动与长期影响"])),
            "stakeholders": _nonempty_list(scope.get("actors"), ["决策者与受影响者"]),
            "constraints": _nonempty_list(scope.get("constraints"), ["信息、资源与时间约束"]),
            "success_criteria": _nonempty_list(problem.get("success_criteria"), ["结论可被证据更新"]),
        },
        "decomposition": decomposition,
        "knowledge_map": {
            "domains": [_node_entry(node, "提供问题所属的学科视角与证据传统") for node in selected["domains"]],
            "core_nodes": [_node_entry(node, "提供可操作的领域机制与方法") for node in selected["core_nodes"]],
            "thinking_models": [_node_entry(node, "用于检查推理、偏差与权衡") for node in selected["thinking_models"]],
            "universal_models": [_node_entry(node, "用于识别跨领域重复出现的系统结构") for node in selected["universal_models"]],
        },
        "relationships": [
            {
                "source_id": relation["source"],
                "type": relation["type"],
                "target_id": relation["target"],
                "explanation": relation.get("scope", ""),
            }
            for relation in retrieval["relations"][:18]
        ],
        "solution_space": {
            "candidate_solutions": [
                {
                    "title": "低成本基线与信息增益方案",
                    "mechanism": f"先按{workflow[0]['action'] if workflow else '问题定义'}建立基线，再优先消除会改变方案排序的未知。",
                    "prerequisites": ["明确成功标准", "可取得最低限度的基线证据"],
                    "benefits": ["可逆", "降低过早承诺", "暴露关键未知"],
                    "risks": ["短期看起来进展较慢", "可能低估结构性约束"],
                    "evidence_needed": evidence[:2],
                    "reversibility": "高：可在新证据出现后快速调整",
                },
                {
                    "title": "受控试点与反馈学习方案",
                    "mechanism": f"用{thinking_label}设计小规模试点，并以{universal_label}持续更新。",
                    "prerequisites": ["能隔离试点范围", "定义停止、扩大和回滚阈值"],
                    "benefits": ["把争论转为可观察反馈", "兼顾行动与学习"],
                    "risks": ["试点情境可能不代表全面实施", "反馈指标可能被误设"],
                    "evidence_needed": evidence[:3],
                    "reversibility": "中高：在明确回滚条件下逐步扩大",
                },
                {
                    "title": "结构性重构方案",
                    "mechanism": "针对瓶颈、激励、接口或制度约束改变系统结构，而不是只优化表面症状。",
                    "prerequisites": ["确认根因层级", "获得相关主体授权与资源"],
                    "benefits": ["可能解决反复出现的问题", "长期收益更高"],
                    "risks": ["成本与不可逆性更高", "二阶效应和主体反应更强"],
                    "evidence_needed": evidence,
                    "reversibility": "较低：应先通过情景、原型或阶段门降低承诺风险",
                },
            ],
            "comparison_criteria": ["目标达成度", "证据可信度", "成本与机会成本", "风险与最坏情形", "可逆性", "公平与外部性", "长期适应性"],
            "provisional_strategy": "先运行低成本基线与受控试点；只有在关键机制得到区分性证据支持后，才升级为结构性重构。",
        },
        "evidence_plan": {
            "knowns": ["用户已明确提出的问题陈述"],
            "unknowns": _nonempty_list(problem.get("trigger_questions"), ["哪些未知会改变方案排序？"]),
            "tests": evidence,
            "escalation_conditions": _nonempty_list(problem.get("escalation_conditions"), ["当风险、不可逆性或专业责任超过当前能力边界时升级"]),
        },
        "next_actions": [
            {
                "order": index + 1,
                "action": step["action"],
                "output": step["output"],
                "decision_gate": step["gate"],
            }
            for index, step in enumerate(workflow)
        ],
        "caveats": [
            problem.get("boundary_notes") or "该框架提供求解结构，不替代特定领域的专业判断。",
            "图谱用于扩大和组织问题空间；最终结论仍需现实证据、价值选择与责任主体确认。",
        ],
    }


def _valid_string(value: Any, fallback: str, maximum: int = 1200) -> str:
    return value.strip()[:maximum] if isinstance(value, str) and value.strip() else fallback


def _strings(value: Any, fallback: list[str], limit: int = 12) -> list[str]:
    if not isinstance(value, list):
        return fallback
    return [item.strip()[:600] for item in value if isinstance(item, str) and item.strip()][:limit]


def ground_analysis(
    graph: Graph,
    retrieval: dict[str, Any],
    candidate: Any,
    query: str,
) -> dict[str, Any]:
    base = create_deterministic_analysis(graph, retrieval, query)
    value = candidate if isinstance(candidate, dict) else {}
    allowed = retrieval["allowed_ids"]
    knowledge: dict[str, list[dict[str, str]]] = {}
    incoming_map = value.get("knowledge_map") if isinstance(value.get("knowledge_map"), dict) else {}
    for key in KNOWLEDGE_GROUPS:
        incoming = incoming_map.get(key) if isinstance(incoming_map.get(key), list) else []
        grounded = []
        for item in incoming:
            if not isinstance(item, dict) or item.get("node_id") not in allowed:
                continue
            node_id = item["node_id"]
            grounded.append(
                {
                    "node_id": node_id,
                    "relevance": _valid_string(item.get("relevance"), graph.node_by_id[node_id].get("definition") or "与问题相关"),
                    "role": _valid_string(item.get("role"), "图谱调用节点", 240),
                }
            )
        knowledge[key] = grounded[:12] or base["knowledge_map"][key]

    relation_by_key = {
        (relation["source"], relation["type"], relation["target"]): relation
        for relation in graph.relationships
    }
    relationships = []
    for item in value.get("relationships", []) if isinstance(value.get("relationships"), list) else []:
        if not isinstance(item, dict):
            continue
        key = (item.get("source_id"), item.get("type"), item.get("target_id"))
        if key[0] not in allowed or key[2] not in allowed or key not in relation_by_key:
            continue
        relation = relation_by_key[key]
        relationships.append(
            {
                "source_id": relation["source"],
                "type": relation["type"],
                "target_id": relation["target"],
                "explanation": _valid_string(item.get("explanation"), relation.get("scope", "")),
            }
        )

    incoming_space = value.get("solution_space") if isinstance(value.get("solution_space"), dict) else {}
    normalized_solutions = []
    candidates = incoming_space.get("candidate_solutions") if isinstance(incoming_space.get("candidate_solutions"), list) else []
    for index, item in enumerate(candidates[:8]):
        if not isinstance(item, dict):
            continue
        fallback = base["solution_space"]["candidate_solutions"][index % 3]
        normalized_solutions.append(
            {
                "title": _valid_string(item.get("title"), fallback["title"], 180),
                "mechanism": _valid_string(item.get("mechanism"), fallback["mechanism"]),
                "prerequisites": _strings(item.get("prerequisites"), [], 8),
                "benefits": _strings(item.get("benefits"), [], 8),
                "risks": _strings(item.get("risks"), [], 8),
                "evidence_needed": _strings(item.get("evidence_needed"), [], 8),
                "reversibility": _valid_string(item.get("reversibility"), "需要进一步评估", 240),
            }
        )

    incoming_scope = value.get("scope") if isinstance(value.get("scope"), dict) else {}
    decomposition = []
    incoming_decomposition = value.get("decomposition") if isinstance(value.get("decomposition"), list) else []
    for index, item in enumerate(incoming_decomposition[:12]):
        if not isinstance(item, dict):
            continue
        decomposition.append(
            {
                "id": f"Q{index + 1}",
                "title": _valid_string(item.get("title"), f"子问题 {index + 1}", 180),
                "question": _valid_string(item.get("question"), "需要进一步澄清什么？"),
                "why_it_matters": _valid_string(item.get("why_it_matters"), "它可能改变方案排序。"),
                "depends_on": [node_id for node_id in _strings(item.get("depends_on"), [], 8) if re.fullmatch(r"Q\d+", node_id)],
                "knowledge_node_ids": [node_id for node_id in _strings(item.get("knowledge_node_ids"), [], 8) if node_id in allowed],
            }
        )

    incoming_evidence = value.get("evidence_plan") if isinstance(value.get("evidence_plan"), dict) else {}
    next_actions = []
    incoming_actions = value.get("next_actions") if isinstance(value.get("next_actions"), list) else []
    for index, item in enumerate(incoming_actions[:10]):
        if not isinstance(item, dict):
            continue
        next_actions.append(
            {
                "order": index + 1,
                "action": _valid_string(item.get("action"), f"执行步骤 {index + 1}"),
                "output": _valid_string(item.get("output"), "可检查的阶段产物"),
                "decision_gate": _valid_string(item.get("decision_gate"), "通过后再进入下一步"),
            }
        )

    return {
        "version": "hkm-analysis/1.0",
        "problem_statement": _valid_string(value.get("problem_statement"), query),
        "intent": _valid_string(value.get("intent"), base["intent"]),
        "assumptions": _strings(value.get("assumptions"), base["assumptions"]),
        "scope": {
            "objective": _valid_string(incoming_scope.get("objective"), base["scope"]["objective"]),
            "system_boundary": _valid_string(incoming_scope.get("system_boundary"), base["scope"]["system_boundary"]),
            "time_horizon": _valid_string(incoming_scope.get("time_horizon"), base["scope"]["time_horizon"]),
            "stakeholders": _strings(incoming_scope.get("stakeholders"), base["scope"]["stakeholders"]),
            "constraints": _strings(incoming_scope.get("constraints"), base["scope"]["constraints"]),
            "success_criteria": _strings(incoming_scope.get("success_criteria"), base["scope"]["success_criteria"]),
        },
        "decomposition": decomposition or base["decomposition"],
        "knowledge_map": knowledge,
        "relationships": relationships[:24] or base["relationships"],
        "solution_space": {
            "candidate_solutions": normalized_solutions or base["solution_space"]["candidate_solutions"],
            "comparison_criteria": _strings(incoming_space.get("comparison_criteria"), base["solution_space"]["comparison_criteria"]),
            "provisional_strategy": _valid_string(incoming_space.get("provisional_strategy"), base["solution_space"]["provisional_strategy"]),
        },
        "evidence_plan": {
            "knowns": _strings(incoming_evidence.get("knowns"), base["evidence_plan"]["knowns"]),
            "unknowns": _strings(incoming_evidence.get("unknowns"), base["evidence_plan"]["unknowns"]),
            "tests": _strings(incoming_evidence.get("tests"), base["evidence_plan"]["tests"]),
            "escalation_conditions": _strings(incoming_evidence.get("escalation_conditions"), base["evidence_plan"]["escalation_conditions"]),
        },
        "next_actions": next_actions or base["next_actions"],
        "caveats": _strings(value.get("caveats"), base["caveats"]),
    }
