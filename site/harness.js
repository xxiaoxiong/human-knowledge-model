"use strict";

(() => {
  const ui = {
    health: null,
    sessionId: null,
    conversation: [],
    controller: null,
    turn: 0,
    nodeIndex: new Map(),
    analysis: null,
  };

  const copy = {
    zh: {
      checking: "正在检查 Python Agent…",
      ready: "Agent 已就绪 · 启动配置已载入",
      mock: "交互演示 · 本轮不调用模型",
      offline: "当前是公开图谱模式 · 深度拆解需从 Python 服务打开",
      newConversation: "新对话",
      stop: "停止",
      deepAnalyze: "开始深度拆解",
      conversationTitle: "系统求解对话",
      conversationHint: "Agent 会先检索图谱，再递归分解问题并比较候选满意解。",
      notStarted: "等待问题",
      welcomeTitle: "把问题写具体一点，会得到更好的地图",
      welcomeBody: "说明你想改变什么、受什么限制、谁会受到影响。Agent 会把事实、假设与未知分开，并把关键子问题挂接到真实知识节点。",
      stageRetrieve: "检索图谱",
      stageDecompose: "分解边界",
      stageReason: "比较机制",
      stageGround: "校验落图",
      questionEmpty: "请先写下至少 4 个字符的问题。",
      serviceNeeded: "公开网站不接收模型密钥。请在仓库中配置 .env，运行 Python 服务，再从本地地址使用深度拆解。",
      thinking: "正在推演",
      followup: "继续追问，或补充新的约束……",
      turn: "第 {count} 轮",
      retrieved: "本轮知识调用",
      archetypes: "问题原型",
      domains: "相关领域",
      coreNodes: "领域骨架",
      thinkingModels: "思维模型",
      universalModels: "通用结构",
      relations: "条关系已进入校验",
      framing: "Decision brief",
      problemTree: "问题结构",
      knowledgeMap: "知识调用",
      relationMap: "关键关系",
      solutionSpace: "候选路径",
      evidencePlan: "证据与未知",
      nextActions: "行动顺序",
      objective: "目标",
      boundary: "系统边界",
      horizon: "时间范围",
      stakeholders: "相关主体",
      constraints: "约束",
      success: "成功标准",
      assumptions: "工作假设",
      domainsGroup: "领域",
      coreGroup: "领域骨架",
      thinkingGroup: "Thinking Models",
      universalGroup: "Universal Models",
      why: "为何相关",
      role: "本题角色",
      prerequisites: "前置",
      benefits: "收益",
      risks: "风险",
      evidenceNeeded: "所需证据",
      reversibility: "可逆性",
      provisional: "当前建议",
      compareBy: "比较标准",
      knowns: "当前已知",
      unknowns: "关键未知",
      tests: "证据与测试",
      escalation: "升级条件",
      output: "产物",
      gate: "决策门",
      caveats: "边界提醒",
      copyResult: "复制简报",
      downloadResult: "下载 Markdown",
      copied: "已复制",
      useQuickMatch: "改用图谱快速匹配",
      stopped: "分析已停止。",
      errorTitle: "本轮未完成",
      resetDone: "工作台已清空，可以开始一个新问题。",
      openNode: "查看节点",
      noRelations: "当前检索子图中没有可展示的直接关系。",
      quickShortcut: "匹配路径",
      deepShortcut: "深度拆解",
      studioKicker: "Decision studio",
      studioMotto: "先画地图，再做判断",
      envOnly: "ENV ONLY",
      yourQuestion: "YOUR QUESTION",
      liveContext: "LIVE CONTEXT",
      contextTitle: "本轮调用的知识",
      contextEmptyTitle: "知识会在这里汇合",
      contextEmptyBody: "提交问题后，你会看到命中的问题原型、领域骨架、思维模型和已校验关系。",
      subquestionsMetric: "子问题",
      nodesMetric: "知识节点",
      optionsMetric: "候选路径",
      actionsMetric: "行动门",
      expandDetails: "展开完整分析",
    },
    en: {
      checking: "Checking the Python agent…",
      ready: "Agent ready · startup config loaded",
      mock: "Interactive demo · no model call",
      offline: "Public graph mode · open the Python service for deep analysis",
      newConversation: "New conversation",
      stop: "Stop",
      deepAnalyze: "Start deep analysis",
      conversationTitle: "Systems-solving conversation",
      conversationHint: "The agent retrieves the graph, decomposes the problem, and compares satisfactory candidates.",
      notStarted: "Waiting for a question",
      welcomeTitle: "Specific questions produce better maps",
      welcomeBody: "Describe what you want to change, what constrains you, and who is affected. The agent separates facts, assumptions, and unknowns, then grounds subproblems in real graph nodes.",
      stageRetrieve: "Retrieve graph",
      stageDecompose: "Frame scope",
      stageReason: "Compare mechanisms",
      stageGround: "Ground & verify",
      questionEmpty: "Write a question of at least four characters first.",
      serviceNeeded: "The public site never receives model credentials. Configure .env, start the Python service, and open its local address for deep analysis.",
      thinking: "Reasoning",
      followup: "Ask a follow-up or add a new constraint…",
      turn: "Turn {count}",
      retrieved: "Knowledge in this turn",
      archetypes: "Problem archetypes",
      domains: "Domains",
      coreNodes: "Domain skeletons",
      thinkingModels: "Thinking models",
      universalModels: "Universal structures",
      relations: "relationships verified",
      framing: "Decision brief",
      problemTree: "Problem structure",
      knowledgeMap: "Knowledge calls",
      relationMap: "Key relations",
      solutionSpace: "Candidate paths",
      evidencePlan: "Evidence and unknowns",
      nextActions: "Action sequence",
      objective: "Objective",
      boundary: "System boundary",
      horizon: "Time horizon",
      stakeholders: "Stakeholders",
      constraints: "Constraints",
      success: "Success criteria",
      assumptions: "Working assumptions",
      domainsGroup: "Domains",
      coreGroup: "Domain skeletons",
      thinkingGroup: "Thinking Models",
      universalGroup: "Universal Models",
      why: "Why relevant",
      role: "Role here",
      prerequisites: "Prerequisites",
      benefits: "Benefits",
      risks: "Risks",
      evidenceNeeded: "Evidence needed",
      reversibility: "Reversibility",
      provisional: "Current recommendation",
      compareBy: "Compare by",
      knowns: "Knowns",
      unknowns: "Key unknowns",
      tests: "Evidence and tests",
      escalation: "Escalation conditions",
      output: "Output",
      gate: "Decision gate",
      caveats: "Boundary notes",
      copyResult: "Copy brief",
      downloadResult: "Download Markdown",
      copied: "Copied",
      useQuickMatch: "Use quick graph matching",
      stopped: "Analysis stopped.",
      errorTitle: "This turn did not finish",
      resetDone: "The studio is clear. Start with a new question.",
      openNode: "View node",
      noRelations: "No direct relation is available in the retrieved subgraph.",
      quickShortcut: "Quick match",
      deepShortcut: "Deep analysis",
      studioKicker: "Decision studio",
      studioMotto: "Map first. Judge second.",
      envOnly: "ENV ONLY",
      yourQuestion: "YOUR QUESTION",
      liveContext: "LIVE CONTEXT",
      contextTitle: "Knowledge in this turn",
      contextEmptyTitle: "Knowledge will converge here",
      contextEmptyBody: "After you submit a question, see matched archetypes, domain skeletons, thinking models, and verified relations.",
      subquestionsMetric: "Subproblems",
      nodesMetric: "Knowledge nodes",
      optionsMetric: "Candidate paths",
      actionsMetric: "Action gates",
      expandDetails: "Open full analysis",
    },
  };

  const $ = (selector, context = document) => context.querySelector(selector);
  const $$ = (selector, context = document) => [...context.querySelectorAll(selector)];
  const language = () => document.documentElement.lang.startsWith("zh") ? "zh" : "en";
  const t = (key, values = {}) => Object.entries(values).reduce((text, [name, value]) => text.replaceAll(`{${name}}`, value), copy[language()][key] || key);
  const escapeHTML = (value = "") => String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
  const list = (items, className = "") => `<ul class="${className}">${(items || []).map((item) => `<li>${escapeHTML(item)}</li>`).join("")}</ul>`;
  const graphLabel = (id) => {
    const node = ui.nodeIndex.get(id) || window.HKM?.getNode(id);
    return node?.labels?.[language()] || node?.labels?.zh || node?.labels?.en || id;
  };

  function translateStatic() {
    $$('[data-harness-i18n]').forEach((node) => { node.textContent = t(node.dataset.harnessI18n); });
    $$('[data-harness-i18n-placeholder]').forEach((node) => { node.placeholder = t(node.dataset.harnessI18nPlaceholder); });
    renderHealth();
  }

  function renderHealth() {
    const dot = $("#harness-status-dot");
    const text = $("#harness-status-text");
    const name = $("#harness-agent-name");
    if (!dot || !text || !name) return;
    dot.className = "harness-status-dot";
    if (ui.health?.ok) {
      dot.classList.add(ui.health.mode === "mock" ? "mock" : "ready");
      text.textContent = t(ui.health.mode === "mock" ? "mock" : "ready");
      const agent = ui.health.agent || {};
      name.textContent = ui.health.mode === "mock" ? "HKM Demo Agent" : `${agent.provider || "Codex"} · ${agent.model || "model"}`;
    } else if (ui.health === null) {
      dot.classList.add("checking");
      text.textContent = t("checking");
      name.textContent = "Codex Python Agent";
    } else {
      dot.classList.add("offline");
      text.textContent = t("offline");
      name.textContent = language() === "zh" ? "静态知识图谱" : "Static knowledge graph";
    }
  }

  async function checkHealth() {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 1800);
    try {
      const response = await fetch("./api/health", { cache: "no-store", signal: controller.signal });
      ui.health = response.ok ? await response.json() : false;
    } catch {
      ui.health = false;
    } finally {
      window.clearTimeout(timeout);
      renderHealth();
    }
  }

  function appendMessage(role, title, body, actions = "") {
    const container = $("#harness-messages");
    const article = document.createElement("article");
    article.className = `harness-message ${role}`;
    article.innerHTML = `<span class="message-avatar" aria-hidden="true">${role === "user" ? "YOU" : "HKM"}</span><div><strong>${escapeHTML(title)}</strong><p>${escapeHTML(body)}</p>${actions}</div>`;
    container.append(article);
    article.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function setBusy(busy) {
    $("#harness-send").disabled = busy;
    $("#harness-stop").hidden = !busy;
    $("#problem-analyze").disabled = busy;
    $("#harness-reset").disabled = busy;
    $("#harness-turn-label").textContent = busy ? t("thinking") : ui.turn ? t("turn", { count: ui.turn }) : t("notStarted");
    $("#harness-thread").classList.toggle("is-running", busy);
    $(".problem-studio").classList.toggle("is-running", busy);
  }

  function setStage(stage, message) {
    const panel = $("#harness-progress");
    panel.hidden = false;
    const order = ["retrieve", "decompose", "reason", "ground"];
    const active = Math.max(order.indexOf(stage), 0);
    $$('[data-harness-stage]', panel).forEach((node, index) => {
      node.classList.toggle("active", index === active);
      node.classList.toggle("done", index < active);
    });
    $("#harness-progress-text").textContent = message || "";
  }

  function renderRetrieval(data) {
    const panel = $("#harness-retrieval");
    const groups = [
      ["archetypes", data.problemArchetypes],
      ["domains", data.domains],
      ["coreNodes", data.coreNodes],
      ["thinkingModels", data.thinkingModels],
      ["universalModels", data.universalModels],
    ];
    const nodes = groups.flatMap(([, items]) => items || []);
    nodes.forEach((node) => ui.nodeIndex.set(node.id, node));
    $("#harness-context-count").textContent = String(nodes.length);
    const groupHTML = groups.filter(([, items]) => items?.length).map(([label, items]) => `<section class="context-group"><header><span>${t(label)}</span><small>${items.length}</small></header><div>${items.slice(0, 8).map((node) => `<button type="button" data-hkm-node="${escapeHTML(node.id)}"><span>${escapeHTML(node.code || "HKM")}</span><strong>${escapeHTML(node.labels?.[language()] || node.labels?.zh || node.labels?.en)}</strong></button>`).join("")}</div></section>`).join("");
    panel.innerHTML = `<div class="context-relation-note"><span>${data.relationshipCount}</span><p>${t("relations")}</p></div>${groupHTML}`;
    bindNodeLinks(panel);
  }

  function scopeCard(labelText, value) {
    const content = Array.isArray(value) ? value.join(" · ") : value;
    return `<section><small>${escapeHTML(labelText)}</small><p>${escapeHTML(content || "—")}</p></section>`;
  }

  function knowledgeGroup(title, items, group) {
    return `<section class="harness-knowledge-group"><header><span>${escapeHTML(title)}</span><strong>${items.length}</strong></header><div>${items.map((item) => `<button type="button" data-hkm-node="${escapeHTML(item.node_id)}" data-group="${group}"><small>${escapeHTML(graphLabel(item.node_id))}</small><strong>${escapeHTML(item.role)}</strong><p>${escapeHTML(item.relevance)}</p><span>${t("openNode")} ↗</span></button>`).join("")}</div></section>`;
  }

  function solutionCard(item, index) {
    return `<article class="solution-card"><header><span>${String(index + 1).padStart(2, "0")}</span><div><h4>${escapeHTML(item.title)}</h4><small>${escapeHTML(item.reversibility)}</small></div></header><p>${escapeHTML(item.mechanism)}</p><details><summary>${t("expandDetails")}</summary><div class="solution-detail-grid">${scopeCard(t("prerequisites"), item.prerequisites)}${scopeCard(t("benefits"), item.benefits)}${scopeCard(t("risks"), item.risks)}${scopeCard(t("evidenceNeeded"), item.evidence_needed)}</div></details></article>`;
  }

  function renderResult(analysis) {
    ui.analysis = analysis;
    const result = $("#harness-result");
    const km = analysis.knowledge_map;
    const nodeCount = Object.values(km).flat().length;
    const relationHTML = analysis.relationships.length ? analysis.relationships.map((item) => `<li><div><button type="button" data-hkm-node="${escapeHTML(item.source_id)}">${escapeHTML(graphLabel(item.source_id))}</button><span>${escapeHTML(item.type)}</span><button type="button" data-hkm-node="${escapeHTML(item.target_id)}">${escapeHTML(graphLabel(item.target_id))}</button></div><p>${escapeHTML(item.explanation)}</p></li>`).join("") : `<p>${t("noRelations")}</p>`;
    result.hidden = false;
    result.innerHTML = `<header class="analysis-hero"><div><p class="eyebrow">${t("framing")}</p><h3>${escapeHTML(analysis.problem_statement)}</h3><p>${escapeHTML(analysis.intent)}</p></div><div class="analysis-actions"><button id="harness-copy" type="button">${t("copyResult")}</button><button id="harness-download" type="button">${t("downloadResult")}</button></div></header>
      <div class="analysis-metrics"><section><strong>${analysis.decomposition.length}</strong><span>${t("subquestionsMetric")}</span></section><section><strong>${nodeCount}</strong><span>${t("nodesMetric")}</span></section><section><strong>${analysis.solution_space.candidate_solutions.length}</strong><span>${t("optionsMetric")}</span></section><section><strong>${analysis.next_actions.length}</strong><span>${t("actionsMetric")}</span></section></div>
      <section class="strategy-lead"><small>${t("provisional")}</small><p>${escapeHTML(analysis.solution_space.provisional_strategy)}</p><span>${escapeHTML(analysis.solution_space.comparison_criteria.join(" · "))}</span></section>
      <div class="analysis-scope-grid">${scopeCard(t("objective"), analysis.scope.objective)}${scopeCard(t("boundary"), analysis.scope.system_boundary)}${scopeCard(t("horizon"), analysis.scope.time_horizon)}${scopeCard(t("stakeholders"), analysis.scope.stakeholders)}${scopeCard(t("constraints"), analysis.scope.constraints)}${scopeCard(t("success"), analysis.scope.success_criteria)}</div>
      <section class="analysis-section"><header><span>01</span><div><h3>${t("problemTree")}</h3>${list(analysis.assumptions)}</div></header><ol class="decomposition-tree">${analysis.decomposition.map((item, index) => `<li><span>Q${index + 1}</span><div><h4>${escapeHTML(item.title)}</h4><p>${escapeHTML(item.question)}</p><small>${escapeHTML(item.why_it_matters)}</small><div>${item.knowledge_node_ids.map((id) => `<button type="button" data-hkm-node="${escapeHTML(id)}">${escapeHTML(graphLabel(id))}</button>`).join("")}</div></div></li>`).join("")}</ol></section>
      <section class="analysis-section"><header><span>02</span><div><h3>${t("solutionSpace")}</h3></div></header><div class="solution-grid">${analysis.solution_space.candidate_solutions.map(solutionCard).join("")}</div></section>
      <section class="analysis-section"><header><span>03</span><div><h3>${t("nextActions")}</h3></div></header><ol class="next-action-list">${analysis.next_actions.map((item) => `<li><span>${String(item.order).padStart(2, "0")}</span><div><strong>${escapeHTML(item.action)}</strong><p><b>${t("output")}</b>${escapeHTML(item.output)}</p><p><b>${t("gate")}</b>${escapeHTML(item.decision_gate)}</p></div></li>`).join("")}</ol></section>
      <details class="analysis-deep-dive"><summary><span>${t("expandDetails")}</span><small>${t("knowledgeMap")} · ${t("relationMap")} · ${t("evidencePlan")}</small></summary><div class="analysis-deep-content"><section class="analysis-section"><header><span>04</span><div><h3>${t("knowledgeMap")}</h3></div></header><div class="harness-knowledge-stack">${knowledgeGroup(t("domainsGroup"), km.domains, "domain")}${knowledgeGroup(t("coreGroup"), km.core_nodes, "core")}${knowledgeGroup(t("thinkingGroup"), km.thinking_models, "thinking")}${knowledgeGroup(t("universalGroup"), km.universal_models, "universal")}</div></section><section class="analysis-section"><header><span>05</span><div><h3>${t("relationMap")}</h3></div></header><ol class="analysis-relations">${relationHTML}</ol></section><section class="analysis-section evidence-plan"><header><span>06</span><div><h3>${t("evidencePlan")}</h3></div></header><div>${scopeCard(t("knowns"), analysis.evidence_plan.knowns)}${scopeCard(t("unknowns"), analysis.evidence_plan.unknowns)}${scopeCard(t("tests"), analysis.evidence_plan.tests)}${scopeCard(t("escalation"), analysis.evidence_plan.escalation_conditions)}</div><div class="caveat-card"><strong>${t("caveats")}</strong>${list(analysis.caveats)}</div></section></div></details>`;
    bindNodeLinks(result);
    $("#harness-copy").addEventListener("click", copyAnalysis);
    $("#harness-download").addEventListener("click", downloadAnalysis);
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function bindNodeLinks(context) {
    $$('[data-hkm-node]', context).forEach((button) => button.addEventListener("click", () => window.HKM?.openNode(button.dataset.hkmNode)));
  }

  function markdownAnalysis(analysis) {
    const lines = [`# HKM 问题分析`, "", `## 问题`, analysis.problem_statement, "", `## 意图`, analysis.intent, "", `## 暂定策略`, analysis.solution_space.provisional_strategy, "", `## 问题树`];
    analysis.decomposition.forEach((item) => lines.push(`- **${item.id} ${item.title}**：${item.question}`, `  - ${item.why_it_matters}`));
    lines.push("", `## 候选满意解`);
    analysis.solution_space.candidate_solutions.forEach((item, index) => lines.push(`${index + 1}. **${item.title}**：${item.mechanism}`, `   - 风险：${item.risks.join("；")}`, `   - 证据：${item.evidence_needed.join("；")}`));
    lines.push("", `## 关键未知`, ...analysis.evidence_plan.unknowns.map((item) => `- ${item}`), "", `## 下一步`);
    analysis.next_actions.forEach((item) => lines.push(`${item.order}. ${item.action} → ${item.output}（门：${item.decision_gate}）`));
    lines.push("", `## 图谱调用`, ...Object.values(analysis.knowledge_map).flat().map((item) => `- ${item.node_id} · ${graphLabel(item.node_id)}`), "", `> ${analysis.caveats.join(" ")}`);
    return lines.join("\n");
  }

  async function copyAnalysis(event) {
    const button = event.currentTarget;
    const markdown = markdownAnalysis(ui.analysis);
    try {
      await navigator.clipboard.writeText(markdown);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = markdown;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.append(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
    button.textContent = t("copied");
    window.setTimeout(() => { button.textContent = t("copyResult"); }, 1400);
  }

  function downloadAnalysis() {
    const blob = new Blob([markdownAnalysis(ui.analysis)], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `HKM-analysis-${new Date().toISOString().slice(0, 10)}.md`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async function consumeStream(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      for (const line of lines) if (line.trim()) handleEvent(JSON.parse(line));
      if (done) break;
    }
    if (buffer.trim()) handleEvent(JSON.parse(buffer));
  }

  function handleEvent(event) {
    if (event.type === "session") ui.sessionId = event.sessionId;
    if (event.type === "progress") setStage(event.stage, event.message);
    if (event.type === "retrieval") renderRetrieval(event.data);
    if (event.type === "final") {
      ui.sessionId = event.sessionId;
      renderResult(event.analysis);
      ui.conversation.push({ role: "assistant", content: `${event.analysis.intent} ${event.analysis.solution_space.provisional_strategy}` });
      appendMessage("assistant", t("turn", { count: ui.turn }), event.analysis.solution_space.provisional_strategy);
    }
    if (event.type === "error") throw new Error(event.error);
  }

  async function analyze() {
    const input = $("#problem-input");
    const query = input.value.trim();
    if (query.length < 4) {
      appendMessage("assistant", t("errorTitle"), t("questionEmpty"));
      input.focus();
      return;
    }
    if (!ui.health?.ok) {
      appendMessage("assistant", t("errorTitle"), t("serviceNeeded"), `<button type="button" class="inline-action" data-quick-match>${t("useQuickMatch")}</button>`);
      $('[data-quick-match]', $("#harness-messages").lastElementChild)?.addEventListener("click", () => window.HKM?.quickMatch(query));
      return;
    }
    ui.turn += 1;
    ui.controller = new AbortController();
    ui.conversation.push({ role: "user", content: query });
    appendMessage("user", t("turn", { count: ui.turn }), query);
    $("#harness-result").hidden = true;
    setBusy(true);
    setStage("retrieve", t("stageRetrieve"));
    try {
      const response = await fetch("./api/analyze", {
        method: "POST",
        headers: { "content-type": "application/json" },
        signal: ui.controller.signal,
        body: JSON.stringify({
          query,
          sessionId: ui.sessionId,
          conversation: ui.conversation.slice(0, -1),
        }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || `HTTP ${response.status}`);
      }
      await consumeStream(response);
      input.placeholder = t("followup");
      if (ui.analysis) {
        input.value = "";
        input.dispatchEvent(new Event("input", { bubbles: true }));
      }
    } catch (error) {
      const stopped = error.name === "AbortError";
      appendMessage("assistant", t("errorTitle"), stopped ? t("stopped") : String(error.message || error), `<button type="button" class="inline-action" data-quick-match>${t("useQuickMatch")}</button>`);
      $('[data-quick-match]', $("#harness-messages").lastElementChild)?.addEventListener("click", () => window.HKM?.quickMatch(query));
    } finally {
      ui.controller = null;
      setBusy(false);
    }
  }

  function stopAnalysis() {
    const sessionId = ui.sessionId;
    ui.controller?.abort();
    if (sessionId && ui.health?.ok) {
      fetch("./api/session/stop", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ sessionId }),
      }).catch(() => {});
    }
  }

  function resetContext() {
    $("#harness-context-count").textContent = "0";
    $("#harness-retrieval").innerHTML = `<div class="context-empty"><div class="context-rings" aria-hidden="true"><i></i><i></i><i></i></div><strong>${t("contextEmptyTitle")}</strong><p>${t("contextEmptyBody")}</p></div>`;
  }

  async function resetConversation() {
    stopAnalysis();
    const previous = ui.sessionId;
    ui.sessionId = null;
    ui.conversation = [];
    ui.turn = 0;
    ui.analysis = null;
    ui.nodeIndex.clear();
    $("#harness-result").hidden = true;
    $("#harness-progress").hidden = true;
    $("#harness-messages").innerHTML = "";
    $("#problem-input").value = "";
    $("#problem-input").dispatchEvent(new Event("input", { bubbles: true }));
    resetContext();
    appendMessage("assistant", t("newConversation"), t("resetDone"));
    setBusy(false);
    $("#problem-input").focus();
    if (previous && ui.health?.ok) {
      fetch("./api/session/reset", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ sessionId: previous }),
      }).catch(() => {});
    }
  }

  function setup() {
    $("#harness-send").addEventListener("click", analyze);
    $("#harness-stop").addEventListener("click", stopAnalysis);
    $("#harness-reset").addEventListener("click", resetConversation);
    $("#problem-input").addEventListener("keydown", (event) => {
      if (event.key === "Enter" && (event.ctrlKey || event.metaKey) && event.shiftKey) {
        event.preventDefault();
        analyze();
      }
    });
    window.addEventListener("hkm:language-change", translateStatic);
    translateStatic();
    checkHealth();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup);
  else setup();
})();
