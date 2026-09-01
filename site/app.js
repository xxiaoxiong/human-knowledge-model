"use strict";

const COLORS = ["#5579a7", "#2d7770", "#c49a49", "#de6f52", "#8a617f"];
const state = {
  model: null,
  lang: localStorage.getItem("hkm-language") || "zh",
  activeFilter: "all",
  activeSkeleton: "D03",
  activeModelLayer: "thinking",
  activeProblemFamily: "all",
  activeLearningTier: 50,
  networkNodes: [],
  hoveredDomain: null,
};

const copy = {
  zh: {
    brandTagline: "人类知识模型",
    navMap: "知识地图",
    navBridges: "跨域桥梁",
    navSkeletons: "核心骨架",
    navModels: "思维模型",
    navProblems: "问题映射",
    navLearning: "学习路线",
    navMethod: "如何使用",
    eyebrow: "一张描述人类如何认识世界的开放图谱",
    heroLine1: "知识不是一棵静止的树，",
    heroLine2: "而是一张可以行动的网络。",
    heroLead: "从现实对象、核心问题、证据和方法出发，连接领域、模型、实践与学习路径。树给你入口，图保留真实关系。",
    exploreMap: "探索知识地图",
    howItWorks: "理解模型如何工作 →",
    findEyebrow: "从问题或概念进入",
    findTitle: "在整张图中寻找知识入口",
    searchLabel: "搜索知识模型",
    searchPlaceholder: "搜索：因果、气候、组织、学习……",
    mapEyebrow: "H1 → H2 → H3",
    mapTitle: "从五个入口进入整个人类知识",
    mapIntro: "20 个一级领域是稳定导航，不是互斥领地。点击节点查看核心问题、边界、子领域和桥接关系。",
    networkHint: "悬停识别连接 · 点击打开领域",
    bridgeEyebrow: "Bridge views",
    bridgeTitle: "现实问题穿过学科边界",
    bridgeIntro: "地理、认知、复杂系统与公共卫生不是重复父级，而是把多个领域重新组织成可调用的问题视图。",
    skeletonEyebrow: "10–30 个结构节点 / 领域",
    skeletonTitle: "先掌握骨架，再进入细节",
    skeletonIntro: "骨架不是词表。每个节点都有类型、问题、前置、适用边界和学习优先级；20 个领域现已全部覆盖。",
    modelsEyebrow: "Thinking × Universal",
    modelsTitle: "把跨学科结构变成可调用的思维工具",
    modelsIntro: "Thinking Models 帮你思考，Universal Models 描述跨领域重复出现的世界结构；每个模型都有证据锚点、反例与使用边界。",
    thinkingLayer: "Thinking Models · 思维操作",
    universalLayer: "Universal Models · 世界结构",
    problemsEyebrow: "Problem → Knowledge",
    problemsTitle: "从现实问题生成知识调用栈",
    problemsIntro: "20 个问题原型把目标、系统边界、领域骨架、两层模型、证据门槛和升级条件连接成可复查工作流。",
    learningEyebrow: "Top 50 → 100 → 300",
    learningTitle: "把有限时间投入高杠杆知识",
    learningIntro: "320 项候选按问题覆盖、前置杠杆、跨域广度、风险与日常价值评分，再以领域和模型配额保证认知多样性。",
    roadmapEyebrow: "八阶段螺旋路线",
    roadmapTitle: "用作品和迁移证据完成八阶段共同底座",
    methodEyebrow: "从知道到行动",
    methodTitle: "怎样使用这张知识图谱",
    methodLead: "不从“我该学哪门课”开始，而从“我面对什么问题、需要做到什么”开始。模型帮助你定位对象、补齐前置、组合证据并检查边界。",
    step1Title: "定义问题与成功标准",
    step1Body: "说明目标、时间尺度、受影响者和不可接受后果。",
    step2Title: "划定系统边界",
    step2Body: "识别对象、主体、变量、约束、价值与不确定性。",
    step3Title: "调用知识与桥接视图",
    step3Body: "沿领域、H3、模型、方法和前置关系建立证据链。",
    step4Title: "生成并比较方案",
    step4Body: "检查因果、激励、反馈、二阶效应与替代解释。",
    step5Title: "试验、监测与更新",
    step5Body: "把行动变成可学习循环，保留反证和升级阈值。",
    principlesEyebrow: "设计底线",
    principlesTitle: "模型设计原则",
    principle1: "结构 > 数量",
    principle2: "关系 > 罗列",
    principle3: "迁移 > 学科边界",
    principle4: "显式边界 > 假装完备",
    footerText: "一个可扩展、可审计、机器可读的人类知识图谱。",
    backTop: "回到顶部 ↑",
    loading: "正在展开知识图谱…",
    all: "全部",
    domainsUnit: "个领域",
    h3Unit: "个子领域",
    coreUnit: "个骨架节点",
    bridgeUnit: "个跨域视图",
    relationUnit: "条关系",
    modelUnit: "个跨学科模型",
    problemUnit: "个问题原型",
    learningAssetUnit: "项学习候选",
    coreQuestion: "核心问题",
    boundary: "边界与限制",
    subdomains: "H3 子领域",
    bridgeDomains: "连接领域",
    mechanisms: "共同机制",
    members: "视图成员",
    prerequisites: "学习前置",
    connections: "核心关系",
    roles: "骨架角色",
    learningPriority: "学习优先级",
    noPrerequisite: "无显式前置",
    noResults: "没有找到匹配项。试试更短的概念或领域名称。",
    resultCount: "个结果",
    templateDomain: "模板域",
    releasedSkeleton: "已发布骨架",
    detailDomain: "H2 领域",
    detailSubdomain: "H3 子领域",
    detailBridge: "跨域桥接视图",
    detailCore: "核心骨架节点",
    detailThinking: "思维模型",
    detailUniversal: "通用世界模型",
    detailProblem: "问题—知识模板",
    detailLearning: "学习路线单元",
    coreIdea: "核心思想",
    sourceDomains: "来源领域",
    mechanismAnchors: "机制锚点",
    applicableProblems: "适用问题",
    typicalCases: "典型案例",
    counterexamples: "反例",
    commonMisuses: "常见误用",
    modelRelations: "模型关系",
    coreStructure: "核心结构",
    stateVariables: "状态变量",
    dynamics: "动力学",
    manifestations: "跨域表现",
    failureModes: "失效模式",
    problemFamily: "问题家族",
    primaryAim: "目标类型",
    successCriteria: "成功标准",
    scopingDimensions: "问题边界",
    knowledgeCalls: "知识调用栈",
    evidenceRequirements: "证据门槛",
    workflow: "工作流",
    outputs: "最终输出",
    escalationConditions: "升级条件",
    examplePrompts: "示例问题",
    focusAssets: "重点知识",
    practiceProblems: "练习问题",
    learningOutcomes: "学习成果",
    exercises: "练习",
    exitEvidence: "验收证据",
    estimatedHours: "预计投入",
    coreAsset: "领域骨架",
    thinkingAsset: "思维模型",
    universalAsset: "通用模型",
    rankingMethod: "组合规则",
  },
  en: {
    brandTagline: "A map of how humanity knows",
    navMap: "Knowledge map",
    navBridges: "Bridge views",
    navSkeletons: "Core skeletons",
    navModels: "Thinking models",
    navProblems: "Problem maps",
    navLearning: "Learning path",
    navMethod: "How to use",
    eyebrow: "An open graph of how humanity understands the world",
    heroLine1: "Knowledge is not a static tree,",
    heroLine2: "but a network for action.",
    heroLead: "Connect domains, models, practices and learning paths through real-world objects, questions, evidence and methods. The tree gives entry points; the graph preserves reality.",
    exploreMap: "Explore the knowledge map",
    howItWorks: "See how the model works →",
    findEyebrow: "Enter through a question or concept",
    findTitle: "Find an entry point across the whole graph",
    searchLabel: "Search the knowledge model",
    searchPlaceholder: "Search: causality, climate, organizations, learning…",
    mapEyebrow: "H1 → H2 → H3",
    mapTitle: "Five gateways into human knowledge",
    mapIntro: "Twenty domains are stable navigation points, not exclusive territories. Open a node to inspect its questions, boundaries, subdomains and bridges.",
    networkHint: "Hover to trace · click to open",
    bridgeEyebrow: "Bridge views",
    bridgeTitle: "Real problems cross disciplinary borders",
    bridgeIntro: "Geography, cognition, complex systems and public health are not duplicate parents. They reorganize multiple domains into callable problem views.",
    skeletonEyebrow: "10–30 structural nodes per domain",
    skeletonTitle: "Learn the skeleton before the details",
    skeletonIntro: "A skeleton is not a glossary. Every node has a type, question, prerequisite, boundary and learning priority; all twenty domains are now covered.",
    modelsEyebrow: "Thinking × Universal",
    modelsTitle: "Turn cross-disciplinary structures into callable tools",
    modelsIntro: "Thinking Models guide reasoning; Universal Models describe structures repeated across domains. Every model includes evidence anchors, counterexamples and boundaries.",
    thinkingLayer: "Thinking Models · Cognitive tools",
    universalLayer: "Universal Models · World structures",
    problemsEyebrow: "Problem → Knowledge",
    problemsTitle: "Generate a knowledge stack from a real problem",
    problemsIntro: "Twenty archetypes connect goals and scope to domain skeletons, both model layers, evidence gates, escalation conditions and an auditable workflow.",
    learningEyebrow: "Top 50 → 100 → 300",
    learningTitle: "Invest limited time in high-leverage knowledge",
    learningIntro: "The 320 candidates are scored for problem coverage, prerequisite leverage, cross-domain reach, risk and everyday value, then balanced with domain and model quotas.",
    roadmapEyebrow: "Eight-stage spiral",
    roadmapTitle: "Build the common foundation through artifacts and transfer evidence",
    methodEyebrow: "From knowing to acting",
    methodTitle: "How to use this knowledge graph",
    methodLead: "Start not with “which course should I take?” but with “what problem am I facing and what must I achieve?” The model helps locate objects, restore prerequisites, combine evidence and test boundaries.",
    step1Title: "Define the problem and success",
    step1Body: "State goals, timescale, affected parties and unacceptable outcomes.",
    step2Title: "Set the system boundary",
    step2Body: "Identify objects, agents, variables, constraints, values and uncertainty.",
    step3Title: "Call domains and bridge views",
    step3Body: "Follow domains, H3 scopes, models, methods and prerequisites into an evidence chain.",
    step4Title: "Generate and compare options",
    step4Body: "Check causality, incentives, feedback, second-order effects and rival explanations.",
    step5Title: "Experiment, monitor and update",
    step5Body: "Turn action into a learning loop with disconfirmation and escalation thresholds.",
    principlesEyebrow: "Design commitments",
    principlesTitle: "Model design principles",
    principle1: "Structure > volume",
    principle2: "Relations > lists",
    principle3: "Transfer > disciplines",
    principle4: "Explicit limits > false completeness",
    footerText: "An extensible, auditable and machine-readable graph of human knowledge.",
    backTop: "Back to top ↑",
    loading: "Unfolding the knowledge graph…",
    all: "All",
    domainsUnit: "domains",
    h3Unit: "subdomains",
    coreUnit: "core nodes",
    bridgeUnit: "bridge views",
    relationUnit: "relations",
    modelUnit: "cross-domain models",
    problemUnit: "problem templates",
    learningAssetUnit: "learning candidates",
    coreQuestion: "Core questions",
    boundary: "Boundaries and limits",
    subdomains: "H3 subdomains",
    bridgeDomains: "Connected domains",
    mechanisms: "Unifying mechanisms",
    members: "View members",
    prerequisites: "Prerequisites",
    connections: "Core relations",
    roles: "Skeleton roles",
    learningPriority: "Learning priority",
    noPrerequisite: "No explicit prerequisite",
    noResults: "No matching entries. Try a shorter concept or domain name.",
    resultCount: "results",
    templateDomain: "template domain",
    releasedSkeleton: "published skeleton",
    detailDomain: "H2 domain",
    detailSubdomain: "H3 subdomain",
    detailBridge: "Bridge view",
    detailCore: "Core skeleton node",
    detailThinking: "Thinking model",
    detailUniversal: "Universal model",
    detailProblem: "Problem–knowledge template",
    detailLearning: "Learning roadmap unit",
    coreIdea: "Core idea",
    sourceDomains: "Source domains",
    mechanismAnchors: "Mechanism anchors",
    applicableProblems: "Applicable problems",
    typicalCases: "Typical cases",
    counterexamples: "Counterexamples",
    commonMisuses: "Common misuses",
    modelRelations: "Model relations",
    coreStructure: "Core structure",
    stateVariables: "State variables",
    dynamics: "Dynamics",
    manifestations: "Cross-domain manifestations",
    failureModes: "Failure modes",
    problemFamily: "Problem family",
    primaryAim: "Aim types",
    successCriteria: "Success criteria",
    scopingDimensions: "Problem boundary",
    knowledgeCalls: "Knowledge call stack",
    evidenceRequirements: "Evidence gates",
    workflow: "Workflow",
    outputs: "Final outputs",
    escalationConditions: "Escalation conditions",
    examplePrompts: "Example prompts",
    focusAssets: "Focus assets",
    practiceProblems: "Practice problems",
    learningOutcomes: "Learning outcomes",
    exercises: "Exercises",
    exitEvidence: "Exit evidence",
    estimatedHours: "Estimated effort",
    coreAsset: "Domain skeletons",
    thinkingAsset: "Thinking models",
    universalAsset: "Universal models",
    rankingMethod: "Portfolio rule",
  },
};

const $ = (selector, context = document) => context.querySelector(selector);
const $$ = (selector, context = document) => [...context.querySelectorAll(selector)];
const t = (key) => copy[state.lang][key] || copy.zh[key] || key;
const escapeHTML = (value = "") =>
  String(value).replace(
    /[&<>'"]/g,
    (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char],
  );
const label = (node) => node?.labels?.[state.lang] || node?.labels?.zh || node?.labels?.en || node?.code || "";
const definition = (node) => node?.definition || "";

function problemFamilyLabel(family) {
  const labels = {
    all: { zh: "全部", en: "All" },
    sensemaking: { zh: "理解与诊断", en: "Sensemaking" },
    "prediction-decision": { zh: "预测与决策", en: "Prediction & decision" },
    "design-intervention": { zh: "设计与干预", en: "Design & intervention" },
    "coordination-governance": { zh: "协调与治理", en: "Coordination & governance" },
    "risk-response": { zh: "风险与响应", en: "Risk & response" },
    "learning-meaning": { zh: "学习与意义", en: "Learning & meaning" },
  };
  return labels[family]?.[state.lang] || family;
}

function indexes() {
  const model = state.model;
  return {
    superdomainById: new Map(model.superdomains.map((item, index) => [item.id, { ...item, color: COLORS[index] }])),
    domainById: new Map(model.domains.map((item) => [item.id, item])),
    domainByCode: new Map(model.domains.map((item) => [item.code, item])),
    subdomainById: new Map(model.subdomains.map((item) => [item.id, item])),
    bridgeById: new Map(model.bridges.map((item) => [item.id, item])),
    coreById: new Map(model.coreNodes.map((item) => [item.id, item])),
    thinkingById: new Map(model.thinkingModels.map((item) => [item.id, item])),
    universalById: new Map(model.universalModels.map((item) => [item.id, item])),
    problemById: new Map(model.problemTemplates.map((item) => [item.id, item])),
    learningById: new Map(model.learningUnits.map((item) => [item.id, item])),
    priorityById: new Map(model.learningPriorities.map((item) => [item.node_id, item])),
    modelById: new Map([...model.thinkingModels, ...model.universalModels].map((item) => [item.id, item])),
  };
}

function applyTranslations() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
  $$('[data-i18n]').forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  $$('[data-i18n-placeholder]').forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  $("#language-toggle").textContent = state.lang === "zh" ? "EN" : "中";
}

function renderHero() {
  const { superdomainById } = indexes();
  const container = $("#hero-superdomains");
  container.replaceChildren();
  state.model.superdomains.forEach((superdomain, index) => {
    const angle = -90 + index * 72;
    const radians = (angle * Math.PI) / 180;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "orbit-node";
    button.style.left = `${50 + Math.cos(radians) * 42}%`;
    button.style.top = `${50 + Math.sin(radians) * 42}%`;
    button.style.setProperty("--node-color", superdomainById.get(superdomain.id).color);
    button.innerHTML = `<span>${escapeHTML(superdomain.code)}</span><strong>${escapeHTML(label(superdomain))}</strong>`;
    button.addEventListener("click", () => {
      state.activeFilter = superdomain.id;
      renderFilters();
      renderDomainGroups();
      $("#map").scrollIntoView({ behavior: "smooth" });
    });
    container.append(button);
  });

  const counts = state.model.meta.counts;
  const stats = [
    [counts.domains, t("domainsUnit")],
    [counts.subdomains, t("h3Unit")],
    [counts.bridges, t("bridgeUnit")],
    [counts.coreNodes, t("coreUnit")],
    [counts.thinkingModels + counts.universalModels, t("modelUnit")],
    [counts.problemTemplates, t("problemUnit")],
    [counts.learningCandidates, t("learningAssetUnit")],
    [counts.relations, t("relationUnit")],
  ];
  $("#stat-ribbon").innerHTML = stats
    .map(([number, unit]) => `<div class="stat-item"><strong>${number}</strong><span>${escapeHTML(unit)}</span></div>`)
    .join("");
}

function renderFilters() {
  const { superdomainById } = indexes();
  const container = $("#superdomain-filters");
  const items = [{ id: "all", labels: { zh: "全部", en: "All" } }, ...state.model.superdomains];
  container.innerHTML = items
    .map((item) => {
      const color = item.id === "all" ? "var(--ink)" : superdomainById.get(item.id).color;
      return `<button type="button" class="filter-chip" data-filter="${escapeHTML(item.id)}" aria-pressed="${state.activeFilter === item.id}" style="--filter-color:${color}">${escapeHTML(label(item))}</button>`;
    })
    .join("");
  $$("[data-filter]", container).forEach((button) => {
    button.addEventListener("click", () => {
      state.activeFilter = button.dataset.filter;
      renderFilters();
      renderDomainGroups();
      drawNetwork();
    });
  });
}

function renderDomainGroups() {
  const { superdomainById } = indexes();
  const container = $("#domain-groups");
  const visible = state.model.superdomains.filter(
    (item) => state.activeFilter === "all" || state.activeFilter === item.id,
  );
  container.innerHTML = visible
    .map((superdomain) => {
      const meta = superdomainById.get(superdomain.id);
      const domains = state.model.domains.filter((domain) => domain.parent === superdomain.id);
      const cards = domains
        .map((domain) => {
          const h3Count = state.model.subdomains.filter((item) => item.parent === domain.id).length;
          const coreCount = state.model.coreNodes.filter((item) => item.primary_domain === domain.id).length;
          const countCopy = `${h3Count} H3${coreCount ? ` · ${coreCount} ${t("coreUnit")}` : ""}`;
          return `<button type="button" class="domain-card" data-open-kind="domain" data-open-id="${escapeHTML(domain.id)}" style="--card-color:${meta.color}">
            <span class="domain-card-top"><span>${escapeHTML(domain.code)}</span><span class="domain-count">${escapeHTML(countCopy)}</span></span>
            <strong>${escapeHTML(label(domain))}</strong>
            <p>${escapeHTML(definition(domain))}</p>
            <span class="card-arrow" aria-hidden="true">↗</span>
          </button>`;
        })
        .join("");
      return `<section class="domain-group" id="group-${escapeHTML(superdomain.code)}" style="--group-color:${meta.color}">
        <div class="group-heading">
          <span class="group-code">${escapeHTML(superdomain.code)}</span>
          <h3>${escapeHTML(label(superdomain))}</h3>
          <p>${escapeHTML(definition(superdomain))}</p>
        </div>
        <div class="domain-card-grid">${cards}</div>
      </section>`;
    })
    .join("");
  bindOpenButtons(container);
}

function renderBridges() {
  const container = $("#bridge-grid");
  container.innerHTML = state.model.bridges
    .map(
      (bridge) => `<button type="button" class="bridge-card" data-open-kind="bridge" data-open-id="${escapeHTML(bridge.id)}">
        <span class="bridge-number">${escapeHTML(bridge.code)} · ${bridge.members.length} H3</span>
        <strong>${escapeHTML(label(bridge))}</strong>
        <p>${escapeHTML(definition(bridge))}</p>
        <span class="domain-dots">${bridge.member_domains.map((code) => `<span class="domain-dot">${escapeHTML(code)}</span>`).join("")}</span>
      </button>`,
    )
    .join("");
  bindOpenButtons(container);
}

function renderSkeletons() {
  const { domainById, superdomainById } = indexes();
  const domainIds = [...new Set(state.model.coreNodes.map((node) => node.primary_domain))];
  const domains = domainIds.map((id) => domainById.get(id)).sort((a, b) => a.code.localeCompare(b.code));
  if (!domains.some((domain) => domain.code === state.activeSkeleton)) {
    state.activeSkeleton = domains[0]?.code;
  }
  const tabs = $("#skeleton-tabs");
  tabs.innerHTML = domains
    .map((domain) => {
      const color = superdomainById.get(domain.parent).color;
      return `<button type="button" role="tab" class="skeleton-tab" data-skeleton="${escapeHTML(domain.code)}" aria-selected="${state.activeSkeleton === domain.code}" style="--tab-color:${color}">${escapeHTML(domain.code)} · ${escapeHTML(label(domain))}</button>`;
    })
    .join("");
  $$("[data-skeleton]", tabs).forEach((button) => {
    button.addEventListener("click", () => {
      state.activeSkeleton = button.dataset.skeleton;
      renderSkeletons();
    });
  });

  const domain = domains.find((item) => item.code === state.activeSkeleton);
  if (!domain) return;
  const color = superdomainById.get(domain.parent).color;
  const nodes = state.model.coreNodes
    .filter((node) => node.primary_domain === domain.id)
    .sort((a, b) => a.code.localeCompare(b.code));
  const priorities = nodes.reduce((result, node) => {
    result[node.learning_priority] = (result[node.learning_priority] || 0) + 1;
    return result;
  }, {});
  $("#skeleton-panel").style.setProperty("--skeleton-color", color);
  $("#skeleton-panel").innerHTML = `<div class="skeleton-summary">
      <span class="big-code">${escapeHTML(domain.code)}</span>
      <h3>${escapeHTML(label(domain))}</h3>
      <p>${escapeHTML(definition(domain))}</p>
      <div class="priority-legend">
        ${Object.entries(priorities)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([priority, count]) => `<div><span class="priority-badge">${priority}</span><span>${count} ${escapeHTML(t("coreUnit"))}</span></div>`)
          .join("")}
      </div>
    </div>
    <div class="core-list">
      ${nodes
        .map(
          (node) => `<button type="button" class="core-node" data-open-kind="core" data-open-id="${escapeHTML(node.id)}">
            <span class="core-code">${escapeHTML(node.code)}</span>
            <span class="core-label"><strong>${escapeHTML(label(node))}</strong><span>${escapeHTML(node.primary_type)} · ${escapeHTML(node.roles.join(" / "))}</span></span>
            <span class="priority-badge">${escapeHTML(node.learning_priority)}</span>
          </button>`,
        )
        .join("")}
    </div>`;
  bindOpenButtons($("#skeleton-panel"));
}

function renderModels() {
  const { domainById } = indexes();
  const layers = [
    { id: "thinking", label: t("thinkingLayer"), models: state.model.thinkingModels },
    { id: "universal", label: t("universalLayer"), models: state.model.universalModels },
  ];
  const tabs = $("#model-layer-tabs");
  tabs.innerHTML = layers
    .map(
      (layer) => `<button type="button" role="tab" class="model-layer-tab" data-model-layer="${layer.id}" aria-selected="${state.activeModelLayer === layer.id}"><span>${escapeHTML(layer.label)}</span><strong>${layer.models.length}</strong></button>`,
    )
    .join("");
  $$('[data-model-layer]', tabs).forEach((button) => {
    button.addEventListener("click", () => {
      state.activeModelLayer = button.dataset.modelLayer;
      renderModels();
    });
  });

  const active = layers.find((layer) => layer.id === state.activeModelLayer) || layers[0];
  $("#model-grid").innerHTML = active.models
    .slice()
    .sort((a, b) => a.code.localeCompare(b.code))
    .map((model) => {
      const domainIds = active.id === "thinking"
        ? model.source_domains
        : model.manifestations.map((item) => item.domain);
      const domains = [...new Set(domainIds)]
        .map((id) => domainById.get(id))
        .filter(Boolean)
        .map((domain) => domain.code);
      const summary = model.core_idea || model.core_structure;
      return `<button type="button" class="model-card ${active.id}" data-open-kind="${active.id}" data-open-id="${escapeHTML(model.id)}">
        <span class="model-card-top"><span>${escapeHTML(model.code)}</span><span class="priority-badge">${escapeHTML(model.learning_priority)}</span></span>
        <strong>${escapeHTML(label(model))}</strong>
        <p>${escapeHTML(summary)}</p>
        <span class="domain-dots">${domains.map((code) => `<span class="domain-dot">${escapeHTML(code)}</span>`).join("")}</span>
      </button>`;
    })
    .join("");
  bindOpenButtons($("#model-grid"));
}

function renderProblems() {
  const families = [
    "all",
    "sensemaking",
    "prediction-decision",
    "design-intervention",
    "coordination-governance",
    "risk-response",
    "learning-meaning",
  ];
  const tabs = $("#problem-family-tabs");
  tabs.innerHTML = families
    .map((family) => {
      const count = family === "all"
        ? state.model.problemTemplates.length
        : state.model.problemTemplates.filter((item) => item.problem_family === family).length;
      return `<button type="button" role="tab" class="problem-family-tab" data-problem-family="${escapeHTML(family)}" aria-selected="${state.activeProblemFamily === family}"><span>${escapeHTML(problemFamilyLabel(family))}</span><strong>${count}</strong></button>`;
    })
    .join("");
  $$('[data-problem-family]', tabs).forEach((button) => {
    button.addEventListener("click", () => {
      state.activeProblemFamily = button.dataset.problemFamily;
      renderProblems();
    });
  });

  const problems = state.model.problemTemplates
    .filter((item) => state.activeProblemFamily === "all" || item.problem_family === state.activeProblemFamily)
    .sort((a, b) => a.code.localeCompare(b.code));
  $("#problem-grid").innerHTML = problems
    .map((problem) => {
      const calls = problem.knowledge_calls;
      return `<button type="button" class="problem-card" data-open-kind="problem" data-open-id="${escapeHTML(problem.id)}">
        <span class="problem-card-top"><span>${escapeHTML(problem.code)}</span><span class="priority-badge">${escapeHTML(problem.learning_priority)}</span></span>
        <small>${escapeHTML(problemFamilyLabel(problem.problem_family))} · ${escapeHTML(problem.primary_aim)}</small>
        <strong>${escapeHTML(label(problem))}</strong>
        <p>${escapeHTML(definition(problem))}</p>
        <span class="problem-call-counts"><span>${calls.domains.length} H2</span><span>${calls.thinking_models.length} TM</span><span>${calls.universal_models.length} UM</span></span>
      </button>`;
    })
    .join("");
  bindOpenButtons($("#problem-grid"));
}

function learningAssetKind(assetType) {
  return {
    "core-node": "core",
    "thinking-model": "thinking",
    "universal-model": "universal",
  }[assetType];
}

function learningAssetTypeLabel(assetType) {
  return {
    "core-node": t("coreAsset"),
    "thinking-model": t("thinkingAsset"),
    "universal-model": t("universalAsset"),
  }[assetType] || assetType;
}

function renderLearning() {
  const tiers = [50, 100, 300];
  const tabs = $("#learning-tier-tabs");
  tabs.innerHTML = tiers
    .map(
      (tier) => `<button type="button" role="tab" class="learning-tier-tab" data-learning-tier="${tier}" aria-selected="${state.activeLearningTier === tier}"><span>Top ${tier}</span><strong>${tier}</strong></button>`,
    )
    .join("");
  $$('[data-learning-tier]', tabs).forEach((button) => {
    button.addEventListener("click", () => {
      state.activeLearningTier = Number(button.dataset.learningTier);
      renderLearning();
    });
  });

  const entries = state.model.learningPriorities
    .filter((entry) => entry.rank <= state.activeLearningTier)
    .sort((a, b) => a.rank - b.rank);
  const typeCounts = entries.reduce((result, entry) => {
    result[entry.asset_type] = (result[entry.asset_type] || 0) + 1;
    return result;
  }, {});
  $("#learning-tier-summary").innerHTML = ["core-node", "thinking-model", "universal-model"]
    .map((assetType) => `<div><strong>${typeCounts[assetType] || 0}</strong><span>${escapeHTML(learningAssetTypeLabel(assetType))}</span></div>`)
    .join("");

  $("#learning-ranking").innerHTML = entries
    .map((entry) => {
      const kind = learningAssetKind(entry.asset_type);
      return `<button type="button" class="learning-rank-row" data-open-kind="${kind}" data-open-id="${escapeHTML(entry.node_id)}">
        <span class="learning-rank">${entry.rank}</span>
        <span class="learning-rank-label"><small>${escapeHTML(entry.code)} · ${escapeHTML(learningAssetTypeLabel(entry.asset_type))}</small><strong>${escapeHTML(label(entry))}</strong></span>
        <span class="learning-score">${Number(entry.raw_score).toFixed(1)}</span>
      </button>`;
    })
    .join("");
  bindOpenButtons($("#learning-ranking"));

  $("#roadmap-grid").innerHTML = state.model.learningUnits
    .slice()
    .sort((a, b) => a.sequence - b.sequence)
    .map(
      (unit) => `<button type="button" class="roadmap-card" data-open-kind="learning" data-open-id="${escapeHTML(unit.id)}">
        <span class="roadmap-card-top"><span>${escapeHTML(unit.code)}</span><span>${escapeHTML(unit.estimated_hours)} h</span></span>
        <strong>${escapeHTML(label(unit))}</strong>
        <p>${escapeHTML(definition(unit))}</p>
        <span class="roadmap-card-meta"><span>${unit.focus_assets.length} ${escapeHTML(t("learningAssetUnit"))}</span><span>${unit.practice_problems.length} ${escapeHTML(t("problemUnit"))}</span></span>
      </button>`,
    )
    .join("");
  bindOpenButtons($("#roadmap-grid"));
}

function bindOpenButtons(context = document) {
  $$('[data-open-kind]', context).forEach((button) => {
    button.addEventListener("click", () => openDetail(button.dataset.openKind, button.dataset.openId));
  });
}

function detailBlock(title, content, className = "") {
  return `<section class="detail-block ${className}"><h3>${escapeHTML(title)}</h3>${content}</section>`;
}

function questionList(items = []) {
  return `<ul>${items.map((item) => `<li>${escapeHTML(item)}</li>`).join("")}</ul>`;
}

function tagCloud(items = []) {
  return `<div class="tag-cloud">${items.map((item) => `<span class="tag">${escapeHTML(item)}</span>`).join("")}</div>`;
}

function openDetail(kind, id, updateHash = true) {
  const idx = indexes();
  const dialog = $("#detail-dialog");
  let node;
  let html = "";
  let kicker = "";
  let color = "var(--coral)";

  if (kind === "domain") {
    node = idx.domainById.get(id) || idx.domainByCode.get(id);
    if (!node) return;
    const superdomain = idx.superdomainById.get(node.parent);
    color = superdomain.color;
    kicker = `${t("detailDomain")} · ${node.code}`;
    const subdomains = state.model.subdomains.filter((item) => item.parent === node.id);
    const coreNodes = state.model.coreNodes.filter((item) => item.primary_domain === node.id);
    html = detailHeader(node);
    html += detailBlock(t("coreQuestion"), questionList(node.core_questions));
    html += detailBlock(
      t("subdomains"),
      `<div class="detail-list">${subdomains
        .map(
          (item) => `<button type="button" data-open-kind="subdomain" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong><small>${escapeHTML(item.core_questions[0] || "")}</small></button>`,
        )
        .join("")}</div>`,
    );
    if (coreNodes.length) {
      html += detailBlock(
        t("releasedSkeleton"),
        `<div class="detail-list">${coreNodes
          .map(
            (item) => `<button type="button" data-open-kind="core" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong><small>${escapeHTML(item.primary_type)} · ${escapeHTML(item.learning_priority)}</small></button>`,
          )
          .join("")}</div>`,
      );
    }
    html += detailBlock(t("bridgeDomains"), tagCloud(node.bridge_domains || []));
    html += detailBlock(t("boundary"), `<p class="boundary-note">${escapeHTML(node.boundary_notes)}</p>`);
  } else if (kind === "subdomain") {
    node = idx.subdomainById.get(id);
    if (!node) return;
    const parent = idx.domainById.get(node.parent);
    color = idx.superdomainById.get(parent.parent).color;
    kicker = `${t("detailSubdomain")} · ${node.code} · ${parent.code}`;
    html = detailHeader(node);
    html += detailBlock(t("coreQuestion"), questionList(node.core_questions));
    html += detailBlock(t("bridgeDomains"), tagCloud(node.bridge_domains || []));
    html += detailBlock(t("boundary"), `<p class="boundary-note">${escapeHTML(node.boundary_notes)}</p>`);
  } else if (kind === "bridge") {
    node = idx.bridgeById.get(id);
    if (!node) return;
    kicker = `${t("detailBridge")} · ${node.code}`;
    const members = node.members.map((memberId) => idx.subdomainById.get(memberId)).filter(Boolean);
    html = detailHeader(node);
    html += detailBlock(t("coreQuestion"), questionList(node.core_questions));
    html += detailBlock(t("mechanisms"), tagCloud(node.unifying_mechanisms));
    html += detailBlock(t("bridgeDomains"), tagCloud(node.member_domains));
    html += detailBlock(
      t("members"),
      `<div class="detail-list">${members
        .map(
          (item) => `<button type="button" data-open-kind="subdomain" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong><small>${escapeHTML(item.core_questions[0] || "")}</small></button>`,
        )
        .join("")}</div>`,
    );
    html += detailBlock(t("boundary"), `<p class="boundary-note">${escapeHTML(node.boundary_notes)}</p>`);
  } else if (kind === "core") {
    node = idx.coreById.get(id);
    if (!node) return;
    const domain = idx.domainById.get(node.primary_domain);
    color = idx.superdomainById.get(domain.parent).color;
    kicker = `${t("detailCore")} · ${node.code} · ${domain.code}`;
    const prereqs = node.prerequisites.map((prereqId) => idx.coreById.get(prereqId)).filter(Boolean);
    const related = node.related_subdomains.map((scopeId) => idx.subdomainById.get(scopeId)).filter(Boolean);
    html = detailHeader(node);
    html += detailBlock(t("coreQuestion"), questionList(node.core_questions));
    html += detailBlock(t("learningPriority"), tagCloud([node.learning_priority, node.primary_type]));
    html += detailBlock(t("roles"), tagCloud([...node.roles, ...node.aims, ...node.epistemic_modes]));
    html += detailBlock(
      t("prerequisites"),
      prereqs.length
        ? `<div class="detail-list">${prereqs
            .map(
              (item) => `<button type="button" data-open-kind="core" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong><small>${escapeHTML(item.primary_type)}</small></button>`,
            )
            .join("")}</div>`
        : `<p>${escapeHTML(t("noPrerequisite"))}</p>`,
    );
    html += detailBlock(
      t("subdomains"),
      `<div class="detail-list">${related
        .map(
          (item) => `<button type="button" data-open-kind="subdomain" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong></button>`,
        )
        .join("")}</div>`,
    );
    html += detailBlock(t("boundary"), `<p class="boundary-note">${escapeHTML(node.boundary_notes)}</p>`);
  } else if (kind === "thinking") {
    node = idx.thinkingById.get(id);
    if (!node) return;
    color = "#de6f52";
    kicker = `${t("detailThinking")} · ${node.code}`;
    const domains = node.source_domains.map((domainId) => idx.domainById.get(domainId)).filter(Boolean);
    const anchors = node.mechanism_core_nodes.map((coreId) => idx.coreById.get(coreId)).filter(Boolean);
    const relatedModels = node.related_models.map((relation) => ({ ...relation, item: idx.modelById.get(relation.target) })).filter((entry) => entry.item);
    html = detailHeader(node);
    html += detailBlock(t("coreIdea"), `<p>${escapeHTML(node.core_idea)}</p>`);
    html += detailBlock(
      t("sourceDomains"),
      `<div class="detail-list">${domains.map((item) => `<button type="button" data-open-kind="domain" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong></button>`).join("")}</div>`,
    );
    html += detailBlock(
      t("mechanismAnchors"),
      `<div class="detail-list">${anchors.map((item) => `<button type="button" data-open-kind="core" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong></button>`).join("")}</div>`,
    );
    html += detailBlock(t("applicableProblems"), questionList(node.applicable_problems));
    html += detailBlock(t("typicalCases"), questionList(node.typical_cases));
    html += detailBlock(t("counterexamples"), questionList(node.counterexamples));
    html += detailBlock(t("commonMisuses"), questionList(node.common_misuses));
    html += detailBlock(
      t("modelRelations"),
      `<div class="detail-list">${relatedModels.map((entry) => `<button type="button" data-open-kind="${entry.item.code.startsWith("TM") ? "thinking" : "universal"}" data-open-id="${escapeHTML(entry.item.id)}"><strong>${escapeHTML(entry.type)} → ${escapeHTML(entry.item.code)} · ${escapeHTML(label(entry.item))}</strong><small>${escapeHTML(entry.scope)}</small></button>`).join("")}</div>`,
    );
    html += detailBlock(t("learningPriority"), tagCloud([node.learning_priority, ...node.epistemic_modes]));
    html += detailBlock(t("boundary"), `<p class="boundary-note">${escapeHTML(node.boundary_notes)}</p>`);
  } else if (kind === "universal") {
    node = idx.universalById.get(id);
    if (!node) return;
    color = "#2d7770";
    kicker = `${t("detailUniversal")} · ${node.code}`;
    const relatedModels = node.related_models.map((relation) => ({ ...relation, item: idx.modelById.get(relation.target) })).filter((entry) => entry.item);
    html = detailHeader(node);
    html += detailBlock(t("coreStructure"), `<p>${escapeHTML(node.core_structure)}</p>`);
    html += detailBlock(t("stateVariables"), tagCloud(node.state_variables));
    html += detailBlock(t("dynamics"), tagCloud(node.dynamics));
    html += detailBlock(
      t("manifestations"),
      `<div class="manifestation-list">${node.manifestations.map((manifestation) => {
        const domain = idx.domainById.get(manifestation.domain);
        const anchors = manifestation.core_nodes.map((coreId) => idx.coreById.get(coreId)).filter(Boolean);
        return `<article class="manifestation-item"><button type="button" data-open-kind="domain" data-open-id="${escapeHTML(domain.id)}"><strong>${escapeHTML(domain.code)} · ${escapeHTML(label(domain))}</strong></button><p>${escapeHTML(manifestation.expression)}</p><div class="tag-cloud">${anchors.map((anchor) => `<button type="button" class="tag" data-open-kind="core" data-open-id="${escapeHTML(anchor.id)}">${escapeHTML(anchor.code)} · ${escapeHTML(label(anchor))}</button>`).join("")}</div></article>`;
      }).join("")}</div>`,
    );
    html += detailBlock(t("failureModes"), questionList(node.failure_modes));
    html += detailBlock(
      t("modelRelations"),
      `<div class="detail-list">${relatedModels.map((entry) => `<button type="button" data-open-kind="${entry.item.code.startsWith("TM") ? "thinking" : "universal"}" data-open-id="${escapeHTML(entry.item.id)}"><strong>${escapeHTML(entry.type)} → ${escapeHTML(entry.item.code)} · ${escapeHTML(label(entry.item))}</strong><small>${escapeHTML(entry.scope)}</small></button>`).join("")}</div>`,
    );
    html += detailBlock(t("learningPriority"), tagCloud([node.learning_priority, ...node.epistemic_modes]));
    html += detailBlock(t("boundary"), `<p class="boundary-note">${escapeHTML(node.boundary_notes)}</p>`);
  } else if (kind === "problem") {
    node = idx.problemById.get(id);
    if (!node) return;
    color = "#c49a49";
    kicker = `${t("detailProblem")} · ${node.code}`;
    const calls = node.knowledge_calls;
    const domainCalls = calls.domains.map((item) => idx.domainById.get(item)).filter(Boolean);
    const coreCalls = calls.core_nodes.map((item) => idx.coreById.get(item)).filter(Boolean);
    const thinkingCalls = calls.thinking_models.map((item) => idx.thinkingById.get(item)).filter(Boolean);
    const universalCalls = calls.universal_models.map((item) => idx.universalById.get(item)).filter(Boolean);
    const callList = (items, callKind) => `<div class="detail-list">${items.map((item) => `<button type="button" data-open-kind="${callKind}" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong><small>${escapeHTML(item.primary_type || "domain")}</small></button>`).join("")}</div>`;
    const scopeLabels = state.lang === "zh"
      ? { objects: "对象", actors: "主体", timescales: "时间", scales: "尺度", values_at_stake: "价值", constraints: "约束" }
      : { objects: "Objects", actors: "Actors", timescales: "Time", scales: "Scale", values_at_stake: "Values", constraints: "Constraints" };
    const workflowLabels = state.lang === "zh"
      ? { stage: "阶段", action: "动作", output: "产物", gate: "检查门" }
      : { stage: "Stage", action: "Action", output: "Output", gate: "Gate" };
    html = detailHeader(node);
    html += detailBlock(t("problemFamily"), tagCloud([problemFamilyLabel(node.problem_family), node.learning_priority]));
    html += detailBlock(t("primaryAim"), tagCloud([node.primary_aim, ...node.secondary_aims]));
    html += detailBlock(t("coreQuestion"), questionList(node.trigger_questions));
    html += detailBlock(t("successCriteria"), questionList(node.success_criteria));
    html += detailBlock(
      t("scopingDimensions"),
      `<div class="scope-grid">${Object.entries(node.scoping_dimensions).map(([key, values]) => `<article><strong>${escapeHTML(scopeLabels[key] || key)}</strong>${tagCloud(values)}</article>`).join("")}</div>`,
    );
    html += detailBlock(
      t("knowledgeCalls"),
      `<div class="call-stack"><section><h4>H2 Domains</h4>${callList(domainCalls, "domain")}</section><section><h4>Core Nodes</h4>${callList(coreCalls, "core")}</section><section><h4>Thinking Models</h4>${callList(thinkingCalls, "thinking")}</section><section><h4>Universal Models</h4>${callList(universalCalls, "universal")}</section></div>`,
    );
    html += detailBlock(t("evidenceRequirements"), questionList(node.evidence_requirements));
    html += detailBlock(
      t("workflow"),
      `<div class="workflow-table"><div class="workflow-row workflow-head"><span>${workflowLabels.stage}</span><span>${workflowLabels.action}</span><span>${workflowLabels.output}</span><span>${workflowLabels.gate}</span></div>${node.workflow.map((step) => `<div class="workflow-row"><strong>${escapeHTML(step.stage)}</strong><span>${escapeHTML(step.action)}</span><span>${escapeHTML(step.output)}</span><span>${escapeHTML(step.gate)}</span></div>`).join("")}</div>`,
    );
    html += detailBlock(t("outputs"), questionList(node.outputs));
    html += detailBlock(t("failureModes"), questionList(node.failure_modes));
    html += detailBlock(t("escalationConditions"), questionList(node.escalation_conditions), "escalation-block");
    html += detailBlock(t("examplePrompts"), questionList(node.example_prompts));
    html += detailBlock(t("boundary"), `<p class="boundary-note">${escapeHTML(node.boundary_notes)}</p>`);
  } else if (kind === "learning") {
    node = idx.learningById.get(id);
    if (!node) return;
    color = "#5579a7";
    kicker = `${t("detailLearning")} · ${node.code}`;
    const prereqs = node.prerequisites.map((item) => idx.learningById.get(item)).filter(Boolean);
    const focusAssets = node.focus_assets.map((item) => idx.priorityById.get(item)).filter(Boolean);
    const practiceProblems = node.practice_problems.map((item) => idx.problemById.get(item)).filter(Boolean);
    html = detailHeader(node);
    html += detailBlock(t("estimatedHours"), tagCloud([`${node.estimated_hours} h`, `${node.focus_assets.length} ${t("learningAssetUnit")}`]));
    html += detailBlock(
      t("prerequisites"),
      prereqs.length
        ? `<div class="detail-list">${prereqs.map((item) => `<button type="button" data-open-kind="learning" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong><small>${escapeHTML(item.estimated_hours)} h</small></button>`).join("")}</div>`
        : `<p>${escapeHTML(t("noPrerequisite"))}</p>`,
    );
    html += detailBlock(
      t("focusAssets"),
      `<div class="detail-list">${focusAssets.map((item) => `<button type="button" data-open-kind="${learningAssetKind(item.asset_type)}" data-open-id="${escapeHTML(item.node_id)}"><strong>#${item.rank} · ${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong><small>${escapeHTML(learningAssetTypeLabel(item.asset_type))} · ${Number(item.raw_score).toFixed(1)}</small></button>`).join("")}</div>`,
    );
    html += detailBlock(
      t("practiceProblems"),
      `<div class="detail-list">${practiceProblems.map((item) => `<button type="button" data-open-kind="problem" data-open-id="${escapeHTML(item.id)}"><strong>${escapeHTML(item.code)} · ${escapeHTML(label(item))}</strong><small>${escapeHTML(problemFamilyLabel(item.problem_family))}</small></button>`).join("")}</div>`,
    );
    html += detailBlock(t("learningOutcomes"), questionList(node.learning_outcomes));
    html += detailBlock(t("exercises"), questionList(node.exercises));
    html += detailBlock(t("exitEvidence"), questionList(node.exit_evidence));
    html += detailBlock(t("boundary"), `<p class="boundary-note">${escapeHTML(node.boundary_notes)}</p>`);
  }

  $("#detail-kicker").textContent = kicker;
  $("#detail-content").innerHTML = html;
  $("#detail-content").style.setProperty("--detail-color", color);
  bindOpenButtons($("#detail-content"));
  if (!dialog.open) dialog.showModal();
  document.body.classList.add("dialog-open");
  if (updateHash) history.replaceState(null, "", `#detail=${kind}:${encodeURIComponent(node.id)}`);
}

function detailHeader(node) {
  return `<header><h2 class="detail-title" id="detail-title">${escapeHTML(label(node))}</h2><p class="detail-en">${escapeHTML(node.labels?.en || "")}</p><p class="detail-definition">${escapeHTML(definition(node))}</p></header>`;
}

function setupDialog() {
  const dialog = $("#detail-dialog");
  dialog.addEventListener("close", () => {
    document.body.classList.remove("dialog-open");
    if (location.hash.startsWith("#detail=")) history.replaceState(null, "", `${location.pathname}${location.search}`);
  });
  dialog.addEventListener("click", (event) => {
    const bounds = dialog.getBoundingClientRect();
    const outside =
      event.clientX < bounds.left ||
      event.clientX > bounds.right ||
      event.clientY < bounds.top ||
      event.clientY > bounds.bottom;
    if (outside) dialog.close();
  });
}

function buildSearchIndex() {
  return [
    ...state.model.domains.map((item) => ({ kind: "domain", item, type: t("detailDomain") })),
    ...state.model.subdomains.map((item) => ({ kind: "subdomain", item, type: t("detailSubdomain") })),
    ...state.model.bridges.map((item) => ({ kind: "bridge", item, type: t("detailBridge") })),
    ...state.model.coreNodes.map((item) => ({ kind: "core", item, type: t("detailCore") })),
    ...state.model.thinkingModels.map((item) => ({ kind: "thinking", item, type: t("detailThinking") })),
    ...state.model.universalModels.map((item) => ({ kind: "universal", item, type: t("detailUniversal") })),
    ...state.model.problemTemplates.map((item) => ({ kind: "problem", item, type: t("detailProblem") })),
    ...state.model.learningUnits.map((item) => ({ kind: "learning", item, type: t("detailLearning") })),
  ].map((entry) => ({
    ...entry,
    haystack: [
      entry.item.code,
      entry.item.id,
      entry.item.labels?.zh,
      entry.item.labels?.en,
      entry.item.definition,
      ...(entry.item.core_questions || []),
      ...(entry.item.scope_includes || []),
      ...(entry.item.unifying_mechanisms || []),
      ...(entry.item.roles || []),
      entry.item.core_idea,
      entry.item.core_structure,
      ...(entry.item.applicable_problems || []),
      ...(entry.item.typical_cases || []),
      ...(entry.item.counterexamples || []),
      ...(entry.item.common_misuses || []),
      ...(entry.item.state_variables || []),
      ...(entry.item.dynamics || []),
      ...(entry.item.failure_modes || []),
      ...(entry.item.manifestations || []).map((item) => item.expression),
      entry.item.problem_family,
      entry.item.primary_aim,
      ...(entry.item.secondary_aims || []),
      ...(entry.item.trigger_questions || []),
      ...(entry.item.success_criteria || []),
      ...(entry.item.evidence_requirements || []),
      ...(entry.item.outputs || []),
      ...(entry.item.escalation_conditions || []),
      ...(entry.item.example_prompts || []),
      ...(entry.item.learning_outcomes || []),
      ...(entry.item.exercises || []),
      ...(entry.item.exit_evidence || []),
    ]
      .join(" ")
      .toLocaleLowerCase(),
  }));
}

function setupSearch() {
  const input = $("#global-search");
  const results = $("#search-results");
  let searchIndex = buildSearchIndex();
  const render = () => {
    const query = input.value.trim().toLocaleLowerCase();
    if (!query) {
      results.hidden = true;
      results.replaceChildren();
      return;
    }
    const tokens = query.split(/\s+/).filter(Boolean);
    const matches = searchIndex.filter((entry) => tokens.every((token) => entry.haystack.includes(token))).slice(0, 12);
    results.hidden = false;
    if (!matches.length) {
      results.innerHTML = `<p class="empty-search">${escapeHTML(t("noResults"))}</p>`;
      return;
    }
    results.innerHTML = matches
      .map(
        ({ kind, item, type }) => `<button type="button" class="search-result" data-open-kind="${kind}" data-open-id="${escapeHTML(item.id)}"><small>${escapeHTML(type)} · ${escapeHTML(item.code || "")}</small><strong>${escapeHTML(label(item))}</strong><span>${escapeHTML(definition(item).slice(0, 74))}${definition(item).length > 74 ? "…" : ""}</span></button>`,
      )
      .join("");
    bindOpenButtons(results);
  };
  input.addEventListener("input", render);
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      event.preventDefault();
      input.focus();
    }
  });
  window.refreshSearch = () => {
    searchIndex = buildSearchIndex();
    render();
  };
}

function setupLanguage() {
  $("#language-toggle").addEventListener("click", () => {
    state.lang = state.lang === "zh" ? "en" : "zh";
    localStorage.setItem("hkm-language", state.lang);
    applyTranslations();
    renderAllDynamic();
    if (window.refreshSearch) window.refreshSearch();
  });
}

function setupTheme() {
  const stored = localStorage.getItem("hkm-theme");
  const preferred = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  document.documentElement.dataset.theme = stored || preferred;
  $("#theme-toggle").addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("hkm-theme", next);
    drawNetwork();
  });
}

function setupNetwork() {
  const canvas = $("#knowledge-network");
  const tooltip = $("#network-tooltip");
  const locate = (event) => {
    const rect = canvas.getBoundingClientRect();
    const point = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    return state.networkNodes.find((node) => Math.hypot(node.x - point.x, node.y - point.y) <= node.radius + 6);
  };
  canvas.addEventListener("mousemove", (event) => {
    const found = locate(event);
    state.hoveredDomain = found?.domain.id || null;
    if (found) {
      tooltip.hidden = false;
      tooltip.textContent = `${found.domain.code} · ${label(found.domain)}`;
      tooltip.style.left = `${Math.min(event.offsetX + 14, canvas.clientWidth - 270)}px`;
      tooltip.style.top = `${Math.max(event.offsetY - 12, 8)}px`;
      canvas.style.cursor = "pointer";
    } else {
      tooltip.hidden = true;
      canvas.style.cursor = "crosshair";
    }
    drawNetwork();
  });
  canvas.addEventListener("mouseleave", () => {
    state.hoveredDomain = null;
    tooltip.hidden = true;
    drawNetwork();
  });
  canvas.addEventListener("click", (event) => {
    const found = locate(event);
    if (found) openDetail("domain", found.domain.id);
  });
  new ResizeObserver(drawNetwork).observe(canvas);
}

function drawNetwork() {
  if (!state.model) return;
  const canvas = $("#knowledge-network");
  const rect = canvas.getBoundingClientRect();
  if (!rect.width || !rect.height) return;
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.round(rect.width * ratio);
  canvas.height = Math.round(rect.height * ratio);
  const context = canvas.getContext("2d");
  context.scale(ratio, ratio);
  context.clearRect(0, 0, rect.width, rect.height);
  const dark = document.documentElement.dataset.theme === "dark";
  const ink = dark ? "#eef1e8" : "#162a2a";
  const muted = dark ? "rgba(238,241,232,.12)" : "rgba(22,42,42,.12)";
  const centers = [
    [0.17, 0.27],
    [0.49, 0.2],
    [0.8, 0.3],
    [0.67, 0.72],
    [0.24, 0.73],
  ];
  const nodeByDomain = new Map();
  state.networkNodes = [];
  state.model.superdomains.forEach((superdomain, groupIndex) => {
    const domains = state.model.domains.filter((domain) => domain.parent === superdomain.id);
    const [cx, cy] = centers[groupIndex];
    const spread = rect.width < 680 ? 56 : 78;
    domains.forEach((domain, index) => {
      const angle = -Math.PI / 2 + (index * Math.PI * 2) / domains.length;
      const node = {
        domain,
        x: rect.width * cx + Math.cos(angle) * spread,
        y: rect.height * cy + Math.sin(angle) * spread * 0.75,
        radius: rect.width < 680 ? 17 : 22,
        color: COLORS[groupIndex],
      };
      nodeByDomain.set(domain.id, node);
      state.networkNodes.push(node);
    });
  });

  const seenEdges = new Set();
  state.model.domainRelations.forEach((relation) => {
    const source = nodeByDomain.get(relation.source);
    const target = nodeByDomain.get(relation.target);
    if (!source || !target) return;
    const key = [source.domain.id, target.domain.id].sort().join("|");
    if (seenEdges.has(key)) return;
    seenEdges.add(key);
    const hover = state.hoveredDomain && [source.domain.id, target.domain.id].includes(state.hoveredDomain);
    const filterActive =
      state.activeFilter === "all" ||
      source.domain.parent === state.activeFilter ||
      target.domain.parent === state.activeFilter;
    context.beginPath();
    context.moveTo(source.x, source.y);
    context.lineTo(target.x, target.y);
    context.strokeStyle = hover ? "#de6f52" : filterActive ? muted : "rgba(120,120,120,.035)";
    context.lineWidth = hover ? 2 : 0.8;
    context.stroke();
  });

  state.networkNodes.forEach((node) => {
    const active = state.activeFilter === "all" || node.domain.parent === state.activeFilter;
    const hover = state.hoveredDomain === node.domain.id;
    context.beginPath();
    context.arc(node.x, node.y, node.radius + (hover ? 4 : 0), 0, Math.PI * 2);
    context.fillStyle = active ? node.color : dark ? "#2b3a39" : "#c9c7c0";
    context.globalAlpha = active ? 1 : 0.4;
    context.fill();
    context.globalAlpha = 1;
    context.fillStyle = "#fffdf8";
    context.font = `800 ${rect.width < 680 ? 9 : 11}px Inter, system-ui`;
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(node.domain.code, node.x, node.y + 0.5);
    if (hover) {
      context.strokeStyle = ink;
      context.lineWidth = 2;
      context.stroke();
    }
  });

  state.model.superdomains.forEach((superdomain, index) => {
    const [cx, cy] = centers[index];
    context.fillStyle = ink;
    context.globalAlpha = state.activeFilter === "all" || state.activeFilter === superdomain.id ? 0.78 : 0.25;
    context.font = `700 ${rect.width < 680 ? 9 : 11}px Inter, system-ui`;
    context.textAlign = "center";
    context.fillText(`${superdomain.code} · ${label(superdomain)}`, rect.width * cx, rect.height * cy - (rect.width < 680 ? 82 : 112));
    context.globalAlpha = 1;
  });
}

function renderAllDynamic() {
  renderHero();
  renderFilters();
  renderDomainGroups();
  renderBridges();
  renderSkeletons();
  renderModels();
  renderProblems();
  renderLearning();
  drawNetwork();
}

function openHashDetail() {
  if (!location.hash.startsWith("#detail=")) return;
  const payload = location.hash.slice(8);
  const separator = payload.indexOf(":");
  if (separator < 0) return;
  const kind = payload.slice(0, separator);
  const id = decodeURIComponent(payload.slice(separator + 1));
  openDetail(kind, id, false);
}

async function init() {
  setupTheme();
  setupLanguage();
  setupDialog();
  try {
    const response = await fetch("./data/model.json");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.model = await response.json();
    applyTranslations();
    renderAllDynamic();
    setupSearch();
    setupNetwork();
    openHashDetail();
    window.addEventListener("hashchange", openHashDetail);
    requestAnimationFrame(() => $("#loading-state").classList.add("done"));
  } catch (error) {
    $("#loading-state").innerHTML = `<p class="error-state">Unable to load the knowledge graph.<br>${escapeHTML(error.message)}</p>`;
  }
}

init();
