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
    provider: {
      kind: localStorage.getItem("hkm-provider-kind") || "session",
      name: localStorage.getItem("hkm-provider-name") || "",
      baseUrl: localStorage.getItem("hkm-provider-base-url") || "",
      model: localStorage.getItem("hkm-provider-model") || "",
      reasoningEffort: localStorage.getItem("hkm-provider-reasoning") || "medium",
      apiKey: "",
    },
  };

  const copy = {
    zh: {
      checking: "正在检查本地 Companion…", ready: "本地 Companion 已就绪", mock: "演示模式 · 不调用模型", offline: "离线图谱模式 · 深度分析需启动本地服务",
      privacyBadge: "密钥仅驻留本次本地会话", configure: "配置模型", newConversation: "新对话", stop: "停止", deepAnalyze: "AI 深度拆解",
      conversationTitle: "系统求解对话", conversationHint: "Harness 会先检索图谱，再递归分解问题、组合跨学科模型并比较候选满意解。", notStarted: "尚未开始",
      welcomeTitle: "先扩大问题空间，再寻找优解", welcomeBody: "输入任意现实问题。我会显式区分目标、边界、主体、约束、事实、假设与未知，并把每个关键子问题挂接到真实知识节点。",
      stageRetrieve: "检索图谱", stageDecompose: "分解问题", stageReason: "比较机制", stageGround: "校验落图", configTitle: "连接你的模型",
      providerMode: "连接方式", providerSession: "本机 Codex 登录（推荐）", providerCustom: "Responses 兼容服务", providerName: "服务名称", modelId: "模型 ID", modelPlaceholder: "留空使用 Codex 当前默认模型",
      reasoningEffort: "推理强度", securityNote: "API Key 不会写入 localStorage、文件或日志，只随本次请求进入受控的 Codex 子进程环境。", saveConfig: "保存本次配置",
      localTitle: "为什么需要本地 Companion？", localBody: "GitHub Pages 只发布静态图谱。模型密钥与 Agent 执行不应放在公开浏览器代码中，因此深度模式由只监听本机的服务承载。", protocolNote: "自定义服务必须兼容 OpenAI Responses API；传统 Chat Completions 接口不能直接驱动当前 Codex Harness。",
      questionEmpty: "请先写下至少 4 个字符的问题。", configureFirst: "请先启动本地 Companion，再从本地页面使用 AI 深度拆解。", thinking: "正在分析", followup: "继续追问", turn: "第 {count} 轮",
      retrieved: "本轮图谱调用", archetypes: "问题原型", domains: "相关领域", models: "模型透镜", relations: "条关系进入校验",
      framing: "问题定义与边界", problemTree: "递归问题树", knowledgeMap: "知识调用栈", relationMap: "关系与链接", solutionSpace: "候选满意解空间", evidencePlan: "证据与未知", nextActions: "下一步行动",
      objective: "目标", boundary: "系统边界", horizon: "时间范围", stakeholders: "相关主体", constraints: "约束", success: "成功标准", assumptions: "工作假设",
      domainsGroup: "领域", coreGroup: "领域骨架", thinkingGroup: "Thinking Models", universalGroup: "Universal Models", why: "为何相关", role: "在本题中的角色",
      prerequisites: "前置", benefits: "收益", risks: "风险", evidenceNeeded: "所需证据", reversibility: "可逆性", provisional: "暂定策略", compareBy: "比较标准",
      knowns: "当前已知", unknowns: "关键未知", tests: "证据与测试", escalation: "升级条件", output: "产物", gate: "决策门", caveats: "边界提醒",
      copyResult: "复制分析", downloadResult: "下载 Markdown", copied: "已复制", useQuickMatch: "改用图谱快速匹配", stopped: "分析已停止。", errorTitle: "本轮未完成", resetDone: "已开始一段新对话。",
      configSaved: "本次模型配置已更新。", openNode: "打开图谱节点", noRelations: "当前检索子图中没有可展示的直接关系。", noKeyStored: "刷新页面后需要重新输入 API Key。", quickShortcut: "匹配路径", deepShortcut: "AI 深度拆解",
    },
    en: {
      checking: "Checking the local companion…", ready: "Local companion is ready", mock: "Demo mode · no model call", offline: "Offline graph mode · start the local service for deep analysis",
      privacyBadge: "Keys stay in this local session", configure: "Configure model", newConversation: "New conversation", stop: "Stop", deepAnalyze: "AI deep analysis",
      conversationTitle: "Systems-solving conversation", conversationHint: "The harness retrieves the graph, recursively decomposes the problem, combines cross-domain models, and compares satisfactory candidates.", notStarted: "Not started",
      welcomeTitle: "Expand the problem space before optimizing", welcomeBody: "Enter any real problem. The harness separates goals, boundaries, actors, constraints, facts, assumptions, and unknowns, then grounds each subproblem in real knowledge nodes.",
      stageRetrieve: "Retrieve graph", stageDecompose: "Decompose", stageReason: "Compare mechanisms", stageGround: "Ground & verify", configTitle: "Connect your model",
      providerMode: "Connection", providerSession: "Local Codex sign-in (recommended)", providerCustom: "Responses-compatible provider", providerName: "Provider name", modelId: "Model ID", modelPlaceholder: "Leave blank to use the current Codex default",
      reasoningEffort: "Reasoning effort", securityNote: "API keys are never written to localStorage, files, or logs. They enter only the controlled Codex child-process environment for this request.", saveConfig: "Save for this session",
      localTitle: "Why a local companion?", localBody: "GitHub Pages publishes the static graph only. Model credentials and agent execution should not live in public browser code, so deep mode runs on a loopback-only service.", protocolNote: "Custom services must implement the OpenAI Responses API; a legacy Chat Completions endpoint cannot directly drive this Codex harness.",
      questionEmpty: "Write a question of at least four characters first.", configureFirst: "Start the local companion, then use deep analysis from the local page.", thinking: "Analyzing", followup: "Continue", turn: "Turn {count}",
      retrieved: "Graph calls this turn", archetypes: "Problem archetypes", domains: "Domains", models: "Model lenses", relations: "relationships verified",
      framing: "Problem framing and scope", problemTree: "Recursive problem tree", knowledgeMap: "Knowledge call stack", relationMap: "Relations and links", solutionSpace: "Candidate satisfactory solution space", evidencePlan: "Evidence and unknowns", nextActions: "Next actions",
      objective: "Objective", boundary: "System boundary", horizon: "Time horizon", stakeholders: "Stakeholders", constraints: "Constraints", success: "Success criteria", assumptions: "Working assumptions",
      domainsGroup: "Domains", coreGroup: "Domain skeletons", thinkingGroup: "Thinking Models", universalGroup: "Universal Models", why: "Why relevant", role: "Role in this problem",
      prerequisites: "Prerequisites", benefits: "Benefits", risks: "Risks", evidenceNeeded: "Evidence needed", reversibility: "Reversibility", provisional: "Provisional strategy", compareBy: "Compare by",
      knowns: "Knowns", unknowns: "Key unknowns", tests: "Evidence and tests", escalation: "Escalation conditions", output: "Output", gate: "Decision gate", caveats: "Boundary notes",
      copyResult: "Copy analysis", downloadResult: "Download Markdown", copied: "Copied", useQuickMatch: "Use quick graph matching", stopped: "Analysis stopped.", errorTitle: "This turn did not finish", resetDone: "Started a new conversation.",
      configSaved: "Model configuration updated for this session.", openNode: "Open graph node", noRelations: "No direct relation is available in the retrieved subgraph.", noKeyStored: "You will need to enter the API key again after refreshing.", quickShortcut: "Quick match", deepShortcut: "AI deep analysis",
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
    if (!dot || !text) return;
    dot.className = "harness-status-dot";
    if (ui.health?.ok) {
      dot.classList.add(ui.health.mode === "mock" ? "mock" : "ready");
      text.textContent = t(ui.health.mode === "mock" ? "mock" : "ready");
    } else if (ui.health === null) {
      dot.classList.add("checking");
      text.textContent = t("checking");
    } else {
      dot.classList.add("offline");
      text.textContent = t("offline");
    }
  }

  async function checkHealth() {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 1600);
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
    $("#harness-configure").disabled = busy;
    $("#harness-turn-label").textContent = busy ? t("thinking") : ui.turn ? t("turn", { count: ui.turn }) : t("notStarted");
    $("#harness-thread").classList.toggle("is-running", busy);
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
    const nodes = [...data.domains, ...data.coreNodes, ...data.thinkingModels, ...data.universalModels];
    nodes.forEach((node) => ui.nodeIndex.set(node.id, node));
    const chips = (items) => items.slice(0, 8).map((node) => `<button type="button" data-hkm-node="${escapeHTML(node.id)}"><span>${escapeHTML(node.code || "HKM")}</span>${escapeHTML(node.labels?.[language()] || node.labels?.zh || node.labels?.en)}</button>`).join("");
    panel.hidden = false;
    panel.innerHTML = `<header><strong>${t("retrieved")}</strong><span>${data.relationshipCount} ${t("relations")}</span></header>
      <div class="retrieval-row"><small>${t("archetypes")}</small>${chips(data.problemArchetypes)}</div>
      <div class="retrieval-row"><small>${t("domains")}</small>${chips(data.domains)}</div>
      <div class="retrieval-row"><small>${t("models")}</small>${chips([...data.thinkingModels, ...data.universalModels])}</div>`;
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
    return `<article class="solution-card"><header><span>0${index + 1}</span><h4>${escapeHTML(item.title)}</h4><small>${escapeHTML(item.reversibility)}</small></header><p>${escapeHTML(item.mechanism)}</p><div class="solution-detail-grid">${scopeCard(t("prerequisites"), item.prerequisites)}${scopeCard(t("benefits"), item.benefits)}${scopeCard(t("risks"), item.risks)}${scopeCard(t("evidenceNeeded"), item.evidence_needed)}</div></article>`;
  }

  function renderResult(analysis) {
    ui.analysis = analysis;
    const result = $("#harness-result");
    const km = analysis.knowledge_map;
    const relationHtml = analysis.relationships.length ? analysis.relationships.map((item) => `<li><button type="button" data-hkm-node="${escapeHTML(item.source_id)}">${escapeHTML(graphLabel(item.source_id))}</button><span>${escapeHTML(item.type)}</span><button type="button" data-hkm-node="${escapeHTML(item.target_id)}">${escapeHTML(graphLabel(item.target_id))}</button><p>${escapeHTML(item.explanation)}</p></li>`).join("") : `<p>${t("noRelations")}</p>`;
    result.hidden = false;
    result.innerHTML = `<header class="analysis-hero"><div><p class="eyebrow">${t("framing")}</p><h3>${escapeHTML(analysis.problem_statement)}</h3><p>${escapeHTML(analysis.intent)}</p></div><div class="analysis-actions"><button id="harness-copy" type="button">${t("copyResult")}</button><button id="harness-download" type="button">${t("downloadResult")}</button></div></header>
      <div class="analysis-scope-grid">${scopeCard(t("objective"), analysis.scope.objective)}${scopeCard(t("boundary"), analysis.scope.system_boundary)}${scopeCard(t("horizon"), analysis.scope.time_horizon)}${scopeCard(t("stakeholders"), analysis.scope.stakeholders)}${scopeCard(t("constraints"), analysis.scope.constraints)}${scopeCard(t("success"), analysis.scope.success_criteria)}</div>
      <section class="analysis-section"><header><span>01</span><div><h3>${t("problemTree")}</h3>${list(analysis.assumptions)}</div></header><ol class="decomposition-tree">${analysis.decomposition.map((item, index) => `<li><span>Q${index + 1}</span><div><h4>${escapeHTML(item.title)}</h4><p>${escapeHTML(item.question)}</p><small>${escapeHTML(item.why_it_matters)}</small><div>${item.knowledge_node_ids.map((id) => `<button type="button" data-hkm-node="${escapeHTML(id)}">${escapeHTML(graphLabel(id))}</button>`).join("")}</div></div></li>`).join("")}</ol></section>
      <section class="analysis-section"><header><span>02</span><div><h3>${t("knowledgeMap")}</h3></div></header><div class="harness-knowledge-stack">${knowledgeGroup(t("domainsGroup"), km.domains, "domain")}${knowledgeGroup(t("coreGroup"), km.core_nodes, "core")}${knowledgeGroup(t("thinkingGroup"), km.thinking_models, "thinking")}${knowledgeGroup(t("universalGroup"), km.universal_models, "universal")}</div></section>
      <section class="analysis-section"><header><span>03</span><div><h3>${t("relationMap")}</h3></div></header><ol class="analysis-relations">${relationHtml}</ol></section>
      <section class="analysis-section"><header><span>04</span><div><h3>${t("solutionSpace")}</h3></div></header><div class="solution-grid">${analysis.solution_space.candidate_solutions.map(solutionCard).join("")}</div><div class="strategy-strip"><small>${t("compareBy")}</small><p>${escapeHTML(analysis.solution_space.comparison_criteria.join(" · "))}</p><strong>${t("provisional")}</strong><p>${escapeHTML(analysis.solution_space.provisional_strategy)}</p></div></section>
      <section class="analysis-section evidence-plan"><header><span>05</span><div><h3>${t("evidencePlan")}</h3></div></header><div>${scopeCard(t("knowns"), analysis.evidence_plan.knowns)}${scopeCard(t("unknowns"), analysis.evidence_plan.unknowns)}${scopeCard(t("tests"), analysis.evidence_plan.tests)}${scopeCard(t("escalation"), analysis.evidence_plan.escalation_conditions)}</div></section>
      <section class="analysis-section"><header><span>06</span><div><h3>${t("nextActions")}</h3></div></header><ol class="next-action-list">${analysis.next_actions.map((item) => `<li><span>${String(item.order).padStart(2, "0")}</span><div><strong>${escapeHTML(item.action)}</strong><p><b>${t("output")}</b>${escapeHTML(item.output)}</p><p><b>${t("gate")}</b>${escapeHTML(item.decision_gate)}</p></div></li>`).join("")}</ol><div class="caveat-card"><strong>${t("caveats")}</strong>${list(analysis.caveats)}</div></section>`;
    bindNodeLinks(result);
    $("#harness-copy").addEventListener("click", copyAnalysis);
    $("#harness-download").addEventListener("click", downloadAnalysis);
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function bindNodeLinks(context) {
    $$('[data-hkm-node]', context).forEach((button) => button.addEventListener("click", () => window.HKM?.openNode(button.dataset.hkmNode)));
  }

  function markdownAnalysis(analysis) {
    const lines = [`# HKM 问题分析`, "", `## 问题`, analysis.problem_statement, "", `## 意图`, analysis.intent, "", `## 问题树`];
    analysis.decomposition.forEach((item) => lines.push(`- **${item.id} ${item.title}**：${item.question}`, `  - ${item.why_it_matters}`));
    lines.push("", `## 候选满意解`);
    analysis.solution_space.candidate_solutions.forEach((item, index) => lines.push(`${index + 1}. **${item.title}**：${item.mechanism}`, `   - 风险：${item.risks.join("；")}`, `   - 证据：${item.evidence_needed.join("；")}`));
    lines.push("", `## 暂定策略`, analysis.solution_space.provisional_strategy, "", `## 关键未知`, ...analysis.evidence_plan.unknowns.map((item) => `- ${item}`), "", `## 下一步`);
    analysis.next_actions.forEach((item) => lines.push(`${item.order}. ${item.action} → ${item.output}（门：${item.decision_gate}）`));
    lines.push("", `## 图谱调用`, ...Object.values(analysis.knowledge_map).flat().map((item) => `- ${item.node_id} · ${graphLabel(item.node_id)}`), "", `> ${analysis.caveats.join(" ")}`);
    return lines.join("\n");
  }

  async function copyAnalysis(event) {
    const button = event.currentTarget;
    const markdown = markdownAnalysis(ui.analysis);
    try {
      await navigator.clipboard.writeText(markdown);
      button.textContent = t("copied");
      window.setTimeout(() => { button.textContent = t("copyResult"); }, 1400);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = markdown;
      textarea.hidden = true;
      document.body.append(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
      button.textContent = t("copied");
      window.setTimeout(() => { button.textContent = t("copyResult"); }, 1400);
    }
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
      appendMessage("assistant", t("errorTitle"), t("configureFirst"), `<button type="button" class="inline-action" data-open-config>${t("configure")}</button>`);
      $('[data-open-config]', $("#harness-messages").lastElementChild)?.addEventListener("click", openConfig);
      openConfig();
      return;
    }
    ui.turn += 1;
    ui.controller = new AbortController();
    ui.conversation.push({ role: "user", content: query });
    appendMessage("user", t("turn", { count: ui.turn }), query);
    $("#harness-result").hidden = true;
    $("#harness-retrieval").hidden = true;
    setBusy(true);
    setStage("retrieve", t("stageRetrieve"));
    try {
      const response = await fetch("./api/analyze", {
        method: "POST",
        headers: { "content-type": "application/json" },
        signal: ui.controller.signal,
        body: JSON.stringify({ query, sessionId: ui.sessionId, conversation: ui.conversation.slice(0, -1), provider: ui.provider }),
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

  function updateConfigFields() {
    const kind = $("#harness-provider-kind").value;
    $("#harness-provider-name-row").hidden = kind !== "custom";
    $("#harness-base-url-row").hidden = !["custom", "ollama"].includes(kind);
    $("#harness-api-key-row").hidden = !["openai", "custom"].includes(kind);
    $("#harness-base-url").required = ["custom", "ollama"].includes(kind);
    $("#harness-api-key").required = kind === "openai";
    $("#harness-model-row").querySelector("input").required = ["custom", "ollama"].includes(kind);
    if (kind === "ollama" && !$("#harness-base-url").value) $("#harness-base-url").value = "http://127.0.0.1:11434/v1";
  }

  function openConfig() {
    $("#harness-provider-kind").value = ui.provider.kind;
    $("#harness-provider-name").value = ui.provider.name;
    $("#harness-base-url").value = ui.provider.baseUrl;
    $("#harness-model").value = ui.provider.model;
    $("#harness-api-key").value = ui.provider.apiKey;
    $("#harness-reasoning").value = ui.provider.reasoningEffort;
    updateConfigFields();
    $("#harness-config-dialog").showModal();
  }

  function saveConfig(event) {
    event.preventDefault();
    ui.provider = {
      kind: $("#harness-provider-kind").value,
      name: $("#harness-provider-name").value.trim(),
      baseUrl: $("#harness-base-url").value.trim(),
      model: $("#harness-model").value.trim(),
      apiKey: $("#harness-api-key").value.trim(),
      reasoningEffort: $("#harness-reasoning").value,
    };
    localStorage.setItem("hkm-provider-kind", ui.provider.kind);
    localStorage.setItem("hkm-provider-name", ui.provider.name);
    localStorage.setItem("hkm-provider-base-url", ui.provider.baseUrl);
    localStorage.setItem("hkm-provider-model", ui.provider.model);
    localStorage.setItem("hkm-provider-reasoning", ui.provider.reasoningEffort);
    ui.sessionId = null;
    $("#harness-config-dialog").close();
    appendMessage("assistant", t("configSaved"), ui.provider.apiKey ? t("noKeyStored") : `${ui.provider.kind} · ${ui.provider.model || "Codex default"}`);
  }

  async function resetConversation() {
    if (ui.controller) ui.controller.abort();
    const previous = ui.sessionId;
    ui.sessionId = null;
    ui.conversation = [];
    ui.turn = 0;
    ui.analysis = null;
    ui.nodeIndex.clear();
    $("#harness-result").hidden = true;
    $("#harness-retrieval").hidden = true;
    $("#harness-progress").hidden = true;
    $("#harness-messages").innerHTML = "";
    appendMessage("assistant", t("newConversation"), t("resetDone"));
    setBusy(false);
    if (previous && ui.health?.ok) fetch("./api/session/reset", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ sessionId: previous }) }).catch(() => {});
  }

  function setup() {
    $("#harness-send").addEventListener("click", analyze);
    $("#harness-stop").addEventListener("click", () => ui.controller?.abort());
    $("#harness-configure").addEventListener("click", openConfig);
    $("#harness-reset").addEventListener("click", resetConversation);
    $("#harness-config-close").addEventListener("click", () => $("#harness-config-dialog").close());
    $("#harness-provider-kind").addEventListener("change", updateConfigFields);
    $("#harness-config-form").addEventListener("submit", saveConfig);
    $("#problem-input").addEventListener("keydown", (event) => {
      if (event.key === "Enter" && (event.ctrlKey || event.metaKey) && event.shiftKey) analyze();
    });
    window.addEventListener("hkm:language-change", translateStatic);
    translateStatic();
    checkHealth();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup);
  else setup();
})();
