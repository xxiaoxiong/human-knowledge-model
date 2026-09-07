# Codex Harness 架构

## 目的

Harness 把任意自然语言问题连接到现有 Human Knowledge Model，再让用户自己的模型在真实图谱上下文中完成对话式分解。它不会让模型自由编造学科或关系：检索层先给出允许使用的节点和边，生成结果随后还要经过确定性的落图校验。

## 两层产品

1. **静态图谱层**：`site/` 和构建出的 `dist-site/`。GitHub Pages 发布这一层，包含 635 个正式节点、3,056 条关系、快速匹配与所有详情浏览能力。
2. **本地 Companion 层**：`harness/server.mjs`。它只监听回环地址，同时托管静态页面和 `/api/*`，因此浏览器与模型服务之间没有跨域配置。

## 一轮请求

1. 浏览器把问题、非敏感模型配置和本轮对话上下文发给 `/api/analyze`。
2. `retrieveGraphContext` 先匹配最多三个问题原型，再沿真实调用关系选出领域、领域骨架、Thinking Models、Universal Models 与相关边。
3. 服务把问题和紧凑检索子图交给官方 `@openai/codex-sdk`。同一会话复用 SDK thread，模型选择与推理强度由用户控制。
4. 模型必须返回 `hkm-analysis/1.0` 的结构化 JSON：问题范围、递归问题树、知识调用、关系、至少三个不同机制的候选方案、证据计划、行动门和边界提醒。
5. `groundAnalysis` 删除不存在或未检索到的节点，关系必须与源图谱的真实有向边一致；若模型漏项，确定性模板会补齐可用结果。
6. 服务通过 NDJSON 流回传检索、分解、推理、校验和最终结果，界面逐步展示进度。

## 连接方式

| 方式 | 认证 | 模型设置 |
|---|---|---|
| 本机 Codex 登录 | 复用本机 Codex 登录状态 | 模型 ID 留空时使用 Codex 当前默认值 |
| OpenAI API Key | 本次页面内存中的 Key | 可留空模型 ID，使用当前默认值 |
| 自定义 Responses 服务 | 可选 API Key | 必填 HTTPS Base URL 与模型 ID |
| Ollama / Local | 通常无需 Key | 默认 `http://127.0.0.1:11434/v1`，必填模型 ID |

自定义 Codex provider 使用 `wire_api = "responses"`。这是 Codex 当前支持的 provider 协议；Chat Completions-only 服务需要先增加 Responses 兼容层。

## 代码入口

- `harness/lib/graph.mjs`：加载、索引、检索与落图校验。
- `harness/lib/prompt.mjs`：问题分解与候选解生成契约。
- `harness/lib/analysis-schema.mjs`：结构化输出 JSON Schema。
- `harness/lib/codex-runner.mjs`：官方 SDK、线程和安全执行选项。
- `harness/lib/provider.mjs`：模型配置验证、密钥隔离与 provider 指纹。
- `site/harness.js`：配置、流式对话和结果呈现。

## 开发与验证

```powershell
pnpm start:mock  # 不调用模型的完整交互演示
pnpm check       # JS 语法、单元/集成测试、构建与站点验证
```

Mock 模式仍然执行真实图谱检索和结果落图，适合开发 UI、CI 和无凭据验收；它只把模型生成步骤替换为确定性分析。
