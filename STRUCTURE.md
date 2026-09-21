# 仓库结构说明（STRUCTURE）

> 本文档用于快速理解 **Agents Towards Production** 仓库的组织方式、目录作用和技术栈。
> 基于仓库实际文件与配置整理，随仓库变动可能需要更新。

---

## 一、项目简介

**Agents Towards Production** 是一个开源教学仓库，不是单一应用程序，而是 **23 个彼此独立、可直接运行的教程** 的合集。目标是把 GenAI Agent 从「原型」做到「生产级」，覆盖编排、记忆、工具、安全、可观测性、评估、部署等各个环节。

- 作者：Nir Diamant
- 许可证：自定义非商用许可（见 [LICENSE](LICENSE)）
- 特点：每个教程一个文件夹，自包含（README + notebook/代码 + 依赖 + 配图），互不 import

---

## 二、顶层目录结构

```
agents-towards-production/
├── README.md              # 主页面：项目介绍 + 教程索引表 + 赞助/课程推广
├── CONTRIBUTING.md        # 贡献规范（规定每个教程的文件结构与质量标准）
├── LICENSE                # 自定义非商用许可证
├── STRUCTURE.md           # 本文档：仓库结构说明
├── .gitignore             # 忽略 .env、venv/、__pycache__ 等
├── .github/               # dependabot.yml / FUNDING.yml / ISSUE_TEMPLATE.md
├── assets/                # 仓库级图片：赞助商 logo、架构图、订阅按钮
├── images/                # README 用到的少量图片
└── tutorials/             # ★ 核心：23 个独立教程 + 1 个 README.md
```

### 各顶层目录/文件的作用

| 路径 | 作用 | 是否核心 |
|---|---|---|
| [README.md](README.md) | 教程地图：按主题分类列出所有教程 + 赞助商信息 | 参考 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 解释单个教程的标准结构，看懂它能快速理解任意教程 | 参考 |
| [tutorials/](tutorials/) | 全部实质内容所在 | ★ 核心 |
| [assets/](assets/) · [images/](images/) | 纯图片/logo 资源 | 可忽略 |
| [.github/](.github/) · [LICENSE](LICENSE) | 工程配置与法务 | 可忽略 |

---

## 三、tutorials/ 教程清单（23 个，按主题）

| 主题 | 教程目录 | 一句话说明 |
|---|---|---|
| **Agent 框架** | [LangGraph-agent](tutorials/LangGraph-agent/) | LangChain 官方：有状态工作流（图结构编排） |
| | [fastapi-agent](tutorials/fastapi-agent/) | 把 Agent 封装成 FastAPI（同步 + 流式接口） |
| | [kotlin-agent-with-koog](tutorials/kotlin-agent-with-koog/) | JetBrains Koog：用 Kotlin 写 Agent |
| **工具 / 数据** | [agent-with-mcp](tutorials/agent-with-mcp/) | 通过 MCP 协议接入外部工具/API |
| | [arcade-secure-tool-calling](tutorials/arcade-secure-tool-calling/) | OAuth2 安全工具调用（Gmail/Slack/Notion） |
| | [agent-with-brightdata](tutorials/agent-with-brightdata/) | Web 数据采集（代理、反爬、结构化抽取） |
| | [agent-with-tavily-web-access](tutorials/agent-with-tavily-web-access/) | 实时 Web 搜索/抓取 |
| | [agent-file-conversion-with-hushvert](tutorials/agent-file-conversion-with-hushvert/) | 本地/私有文件格式转换 |
| **RAG / 知识** | [agent-RAG-with-Contextual](tutorials/agent-RAG-with-Contextual/) | Contextual AI 托管 RAG 平台 |
| **记忆** | [agent-memory-with-redis](tutorials/agent-memory-with-redis/) | 双记忆（短期 Redis list + 长期语义搜索） |
| | [agent-memory-with-mem0](tutorials/agent-memory-with-mem0/) | 自进化记忆（向量 + 图混合） |
| | [ai-memory-with-cognee](tutorials/ai-memory-with-cognee/) | 知识图谱记忆 |
| **多 Agent** | [a2a](tutorials/a2a/) | A2A 协议：多 Agent 通信 |
| **安全** | [agent-security-with-llamafirewall](tutorials/agent-security-with-llamafirewall/) | LlamaFirewall 输入/输出/工具护栏 |
| | [agent-security-apex](tutorials/agent-security-apex/) | 提示注入攻击与防御、自动化安全测试 |
| **可观测 / 评估** | [tracing-with-langsmith](tutorials/tracing-with-langsmith/) | LangSmith 追踪与调试 |
| | [agent-evaluation-intellagent](tutorials/agent-evaluation-intellagent/) | IntellAgent 自动评估 |
| **部署** | [docker-intro](tutorials/docker-intro/) | 用 Docker 容器化 Agent |
| | [on-prem-llm-ollama](tutorials/on-prem-llm-ollama/) | Ollama 本地部署 LLM |
| | [runpod-gpu-deploy](tutorials/runpod-gpu-deploy/) | RunPod GPU 云部署 |
| | [aws_agentcore](tutorials/aws_agentcore/) | AWS Bedrock AgentCore 托管部署 |
| **UI** | [agent-with-streamlit-ui](tutorials/agent-with-streamlit-ui/) | Streamlit 聊天机器人界面 |
| **模型定制** | [fine-tuning-agents](tutorials/fine-tuning-agents/) | 微调模型适配领域 |

---

## 四、单个教程的标准结构

由 [CONTRIBUTING.md](CONTRIBUTING.md) 规定，绝大多数教程遵循：

```
tutorials/<name>/
├── README.md            # 概述：讲什么、动机、能学到什么
├── <name>.ipynb         # 主教程（Jupyter notebook，最常见）
│    或 tutorial.md      # 或 Markdown 教程（配大量截图）
├── app.py               # 可运行代码（部分教程才有）
├── requirements.txt     # Python 依赖（锁版本）
└── assets/              # 截图、图表、视频
```

个别教程结构有差异，例如：
- `fastapi-agent/` 额外有 `scripts/` + `tests/`（唯一带正式测试的教程）
- `kotlin-agent-with-koog/` 是 Gradle 项目结构
- `docker-intro/` 有 5 个 `examples/ex*/Dockerfile`

---

## 五、技术栈

### 编程语言

- **Python**（绝对主力，几乎所有教程）
- **Kotlin**（仅 1 个教程）
- **Jupyter Notebook**（`.ipynb`，主要的「文档 + 代码」载体）
- 辅助：Shell 脚本、Dockerfile、Gradle

### 框架与库（按类别）

| 类别 | 技术 |
|---|---|
| LLM / Agent 框架 | LangChain、LangGraph、OpenAI SDK / openai-agents、JetBrains Koog |
| API 服务 | FastAPI + Uvicorn |
| 前端 UI | Streamlit |
| 记忆 / 向量库 | Redis、Mem0、Cognee、ChromaDB |
| 安全 | LlamaFirewall、Apex |
| 可观测性 | LangSmith |
| 通信协议 | MCP、A2A 协议、OAuth2（Arcade） |
| 数据 / 工具 | pydantic、python-dotenv、pandas、numpy、matplotlib、python-docx、PyPDF2、tavily-python |
| 本地模型 | Ollama |

### 构建 / 包管理 / 部署

- **Python**：`pip` + 每个教程独立的 `requirements.txt`（无统一 pyproject/poetry）
- **Kotlin**：Gradle（`build.gradle.kts` + `gradlew`）
- **依赖自动化**：Dependabot（月度更新 pip 和 github-actions）
- **部署相关**：Docker、AWS Bedrock AgentCore、RunPod（GPU 云）、Ollama（本地）

> 关键点：**没有统一技术栈**。每个教程是独立小项目，各自声明依赖；LangChain/LangGraph + OpenAI 是贯穿大多数教程的主线，各教程再引入主题特有的库。

---

## 六、整体架构

仓库**没有代码层面的架构**——23 个教程互不依赖、无 import 关系。它的「架构」体现在两层：

### ① 仓库组织架构（扁平、完全解耦）

```
README.md（索引 / 地图）
      │  链接到
      ▼
tutorials/  ──► 教程 A（自包含）
               ├─ 教程 B（自包含）
               ├─ 教程 C（自包含）
               └─ ...（23 个，互不依赖）
```

### ② 概念架构（教程共同指向的目标 Agent 技术栈）

```
┌─────────────────────────────────────────────┐
│                生产级 Agent 栈                 │
│                                              │
│  编排 LangGraph                               │
│    ├─ 记忆 Memory（Redis / Mem0 / Cognee）     │
│    ├─ 工具 Tools（MCP / Web搜索 / 文件转换）     │
│    ├─ 安全 Security（护栏 / 防火墙）             │
│    ├─ 可观测 Observability（LangSmith）         │
│    └─ 评估 Evaluation（IntellAgent）           │
│  部署 Deployment（Docker / Ollama / RunPod / AWS）│
│  界面 UI（Streamlit）                          │
└─────────────────────────────────────────────┘
```

**关系**：每个教程 = 覆盖概念架构图中的**一个组件**，靠根 README 的分类把零散教程串成「从原型到生产」的完整学习路径。

---

## 七、本地开发改动（非原始仓库内容）

以下文件是本地环境/学习过程中新增的，**不属于原始仓库**（`git status` 中为未跟踪或被忽略）：

| 文件/目录 | 说明 | 进 git？ |
|---|---|---|
| `tutorials/agent-with-streamlit-ui/app_deepseek.py` | DeepSeek/内网网关适配版（原 `app.py` 是 OpenAI 版） | 未跟踪 |
| `tutorials/agent-with-streamlit-ui/building-chatbot-notebook-zh.ipynb` | 中文翻译版教程 | 未跟踪 |
| `tutorials/agent-with-streamlit-ui/.env` | 存 `DEEPSEEK_API_KEY` | 被忽略 |
| `tutorials/agent-with-streamlit-ui/venv/` | Python 虚拟环境 | 被忽略 |

---

## 八、快速上手 / 推荐阅读顺序

1. 读 [README.md](README.md) 的「Introduction」和「Tutorials」两节 → 拿到主题地图
2. 读 [CONTRIBUTING.md](CONTRIBUTING.md) → 理解单个教程的标准结构
3. 挑一个代表性教程深入：
   - 学核心框架 → [LangGraph-agent](tutorials/LangGraph-agent/)
   - 学 API 化 → [fastapi-agent](tutorials/fastapi-agent/)（唯一带 tests 的工程化教程）
4. 之后按兴趣主题扫其余教程，先看各自的 README 建立概念即可
