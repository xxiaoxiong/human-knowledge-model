# Python Codex Agent 架构

## 目的

Python Agent 把任意自然语言问题连接到现有 Human Knowledge Model，再让启动时配置的模型在真实图谱上下文中完成对话式分解。它可以在本机回环地址运行，也可作为同源 HTTPS 容器服务运行。检索层先给出允许使用的节点和边，生成结果随后还要经过确定性的落图校验。

## 交付形态

1. **静态图谱层**：`site/` 和构建出的 `dist-site/`。GitHub Pages 发布这一层，包含 635 个正式节点、3,056 条关系、快速匹配与所有详情浏览能力。
2. **本地 Agent**：`harness/server.py` 只监听回环地址，同时托管静态页面和 `/api/*`。模型设置在进程启动时从 `.env` 注入。
3. **在线 Agent**：`Dockerfile` 用同一进程提供页面和 API，`render.yaml` 只声明非秘密配置与两个 `sync: false` 秘密项。托管平台在运行时注入模型 Key 和独立站点访问口令。

## 一轮请求

1. 在线模式先用独立站点口令换取 12 小时签名 HttpOnly、Secure、SameSite Cookie；口令不写入浏览器存储。
2. 浏览器只把问题、会话 ID 和有限对话上下文发给 `/api/analyze`；provider、Base URL、模型和 Key 出现在请求中会被拒绝。
3. `retrieve_graph_context` 先匹配最多三个问题原型，再沿真实调用关系选出领域、领域骨架、Thinking Models、Universal Models 与相关边。
4. 服务把问题和紧凑检索子图交给官方 Python `openai-codex` SDK。同一会话复用 SDK thread；模型选择与推理强度只取自启动配置。若 Responses provider 明确以 400 拒绝 SDK 的结构化 `input`，服务会记住该能力差异，并改用字符串 `input` 的服务端 Responses 请求；输出仍使用同一 JSON Schema，浏览器仍看不到模型密钥。
5. 模型必须返回 `hkm-analysis/1.0` 的结构化 JSON：问题范围、递归问题树、知识调用、关系、至少三个不同机制的候选方案、证据计划、行动门和边界提醒。
6. `ground_analysis` 删除不存在或未检索到的节点，关系必须与源图谱的真实有向边一致；若模型漏项，确定性模板会补齐可用结果。
7. 服务通过 NDJSON 流回传检索、分解、推理、校验和最终结果，界面逐步展示进度。

## 启动配置

| 变量 | 必需 | 作用 |
|---|---|---|
| `HKM_MODEL_PROVIDER_NAME` | 是 | 页面显示的非敏感服务标签 |
| `HKM_MODEL_BASE_URL` | 是 | HTTPS Responses API 根地址 |
| `HKM_MODEL_API_KEY` | 是 | 仅供服务端 Codex runtime 或 Responses 兼容请求使用的认证密钥 |
| `HKM_MODEL_ID` | 是 | 启动后固定使用的模型 ID |
| `HKM_MODEL_REASONING_EFFORT` | 否 | 模型支持时设置推理强度 |
| `HKM_HOST` / `HKM_PORT` | 否 | 回环监听地址与端口，默认 `127.0.0.1:4317` |
| `HKM_DEPLOYMENT_MODE` | 否 | `local` 或 `hosted`；默认 `local` |
| `HKM_PUBLIC_ORIGIN` | 托管时 | 精确的公开 HTTPS Origin；Render 可由 `RENDER_EXTERNAL_HOSTNAME` 自动提供 |
| `HKM_ACCESS_TOKEN` | 托管时 | 与模型 Key 分离的至少 32 字符站点口令 |
| `PORT` | 托管时 | 托管平台分配的服务端口 |
| `HKM_RUNTIME_DIR` | 否 | Codex runtime 的可写临时目录 |

自定义 Codex provider 使用 `wire_api = "responses"`。这是 Codex 当前支持的 provider 协议；仅实现字符串 `input` 的 Responses provider 由内置兼容路径处理，Chat Completions-only 服务仍需先增加 Responses 兼容层。配置由 `python-dotenv` 在启动时读取一次；修改 `.env` 必须重启。

## 代码入口

- `harness/settings.py`：启动配置验证与安全的公开摘要。
- `harness/graph.py`：加载、索引、检索、确定性分析与落图校验。
- `harness/prompt.py`：问题分解与候选解生成契约。
- `harness/analysis_schema.py`：结构化输出 JSON Schema。
- `harness/agent.py`：官方 Python SDK、Responses provider、线程与安全执行选项。
- `harness/server.py`：静态服务、API、会话、并发与停止控制。
- `site/harness.js`：交互、流式对话、知识调用与渐进式结果呈现。

## 开发与验证

```powershell
python -m harness.server --mock  # 不调用模型的完整交互演示
pnpm check                      # JS 语法、Python 测试、构建与站点验证
```

Mock 模式仍然执行真实图谱检索和结果落图，适合开发 UI、CI 和无凭据验收；它只把模型生成步骤替换为确定性分析。
