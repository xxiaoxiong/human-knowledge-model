"""Prompt construction for graph-grounded Codex turns."""

from __future__ import annotations

import json
from typing import Any


BASE_INSTRUCTIONS = """你是一个受约束的结构化分析引擎。
直接完成用户要求的分析，只返回 output schema 规定的 JSON。
不得调用任何工具，不得要求审批，不得执行代码或操作文件。"""


DEVELOPER_INSTRUCTIONS = """你是 Human Knowledge Model 的问题求解 Agent。
只处理当前提示中提供的问题、有限对话摘要与 HKM 检索子图。
不要调用 Shell、文件编辑、网页搜索或任何外部工具；不要读取工作区里的其他文件。
区分事实、假设、价值判断、未知与可检验主张。
不得声称已经数学意义上穷尽所有解。高风险、受监管或不可逆问题必须给出升级条件。
最终只返回符合 output schema 的 JSON。"""


def build_prompt(
    *,
    query: str,
    retrieval: dict[str, Any],
    conversation: list[dict[str, str]] | None = None,
) -> str:
    prior = [
        {
            "role": "assistant" if item.get("role") == "assistant" else "user",
            "content": str(item.get("content", ""))[:1200],
        }
        for item in (conversation or [])[-6:]
    ]
    return f"""你正在使用 Human Knowledge Model 把现实问题转换为可检查的认知与行动结构。

工作契约：
1. 先定义目标、边界、主体、尺度、时间与约束，再分解问题。
2. 同时调用领域骨架、Thinking Models 与 Universal Models，并解释节点为什么相连。
3. 至少生成三种机制明显不同的候选满意解；适用时包含不行动、延迟或试点等可逆选项。
4. 给出比较标准、暂定策略、关键未知、证据计划、行动顺序与决策门。
5. knowledge_node_ids、knowledge_map 与 relationships 只能使用检索上下文里出现的真实 HKM ID；关系类型与方向必须和 graph_relationships 一致。
6. 使用用户输入的主要语言，内容具体、简洁、可执行。
7. 最终只返回 JSON，不要输出 Markdown 代码块。

当前问题：
{query}

最近对话（可能为空）：
{json.dumps(prior, ensure_ascii=False)}

HKM 检索上下文：
{json.dumps(retrieval['prompt_context'], ensure_ascii=False)}"""
