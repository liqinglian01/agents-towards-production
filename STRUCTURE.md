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

## 三、tutorials/ 教程清单（23 个）

> 每个教程都是自包含的小项目：`README.md` + 主 notebook（或 Markdown 教程）+ 独立依赖，彼此不 import。
> 每个教程均配有中文版（notebook 为 `*-zh.ipynb`，README 为 `README.zh.md`），中英文双向互链。
> 下面按主题分组，逐个说明 **解决什么问题 / 实现了什么 / 工作流逻辑 / 关键文件 / 外部依赖**。
> 其中「工作流逻辑」拆成四问：**主链路**（运行时按什么顺序发生什么）、**数据流**（关键状态怎么在步骤间传递）、**控制流**（哪儿有分支、判据是什么）、**循环与交互**（哪儿有循环、是哪种交互）。

### 主题一：Agent 框架与编排

#### 1. [LangGraph-agent](tutorials/LangGraph-agent/) — 用「图」编排 Agent
- **解决什么问题**：把多步 LLM 逻辑（分类、抽实体、总结）写死在一次调用里，无法扩展、无法分支。用 LangGraph 的状态图把它拆成可控、可路由的流水线。
- **实现了什么**：
  - 用 `StateGraph` + 共享 state（`text` / `classification` / `entities` / `summary`）串起一条文本分析 pipeline
  - 三个核心节点：**分类**（判断文本类型，如新闻/博客/推文）→ **实体抽取**（人物、组织、地点）→ **摘要生成**
  - 进阶扩展：新增**情感分析**节点，用 `EnhancedState` 承载更多字段
  - **条件边（conditional edges）**：按分类结果动态跳过/执行节点，实现非线性流程
  - 用 Graphviz/mermaid 把工作流画出来，直观看到图的形状
- **工作流逻辑**：
  - **主链路**：`输入 text → classification_node → entity_extraction_node → summarization_node →（增强版再加 sentiment_node）→ END`；条件版在分类后分岔：`classification_node --route_after_classification--> True 走 entity_extraction / False 直接跳 summarization`，两条路径最终都汇合到 `summarization → sentiment_analysis → END`
  - **数据流**：`State` / `EnhancedState` 是唯一状态对象（`text` / `classification` / `entities` / `summary` / `sentiment`）。每个节点只读 `state["text"]` 拼 prompt，返回 `{"字段": 值}` 作为**局部更新**合并回 state；`app.invoke()` 返回完整 state dict，外部按 `result["classification"]` 取值
  - **控制流**：前两个阶段纯线性；第三阶段有 1 个条件边，判据是分类结果是否 `in ["news", "research"]`
  - **循环与交互**：无循环。每次 `invoke()` 都是一次性单遍执行
- **关键文件**：`langgraph_tutorial.ipynb`（主教程：逐步构建 + 可视化 + 条件路由）；`README.md` + `01-mental-model.md` ~ `05-pitfalls.md`（本地新增的**心智模型与拆解方法**指南：讲清图/State/节点、数据流与控制流、自主度阶梯 L0–L3、从需求到图的 5 步拆解法）
- **外部依赖**：OpenAI API key；LangGraph、LangChain、langchain-openai

#### 2. [fastapi-agent](tutorials/fastapi-agent/) — 把 Agent 封装成生产级 HTTP API
- **解决什么问题**：Agent 在 notebook 里能跑，但没法对外提供服务——缺异步、缺流式、缺可测试的接口层。
- **实现了什么**：
  - 用 `SimpleAgent` 类模拟 Agent（同步 + 异步流式两种响应），**不需要真实 LLM**
  - 用 FastAPI + Pydantic 定义 `QueryRequest` / `QueryResponse`，做请求校验与响应结构化
  - 三个端点：`GET /health`（健康检查）、`POST /agent`（同步）、`POST /agent/stream`（`StreamingResponse` + `text/event-stream`，即 **SSE 逐 token 流式输出**）
  - 介绍可选的 `sse-starlette`（更健壮的 SSE 实现）与 Basic Auth 接口保护
  - 用 uvicorn 启动；配 pytest + `TestClient` 写单元测试
- **工作流逻辑**：
  - **主链路**：`HTTP 请求 → 路由分发 →(可选) verify_api_key 鉴权 → SimpleAgent → 响应`，四条独立路径：`GET /health`（直接返回）／`POST /agent`（`generate_response` → `QueryResponse`）／`POST /agent/stream`（`generate_response_stream` 逐 token → `event_generator` 包成 SSE 帧）／`POST /agent/stream-sse`（换 `EventSourceResponse`）
  - **数据流**：`QueryRequest(query, context)` 进 → 字符串出；/stream 路径上每个 token 先 `json.dumps({"token": ...})` 再套成 `data: {...}\n\n` 帧
  - **控制流**：无业务分支，只有 HTTP 路由分发。鉴权函数内是顺序分支：未设环境变量 `API_KEY` → 直接放行；缺 header → `401`；不匹配 → `403`
  - **循环与交互**：`generate_response_stream` 内 `for token in response.split()` 逐 token yield（配 `asyncio.sleep(0.1)` 模拟流式）；客户端 `for line in response.iter_lines()` 解析 SSE。均为单向流式，不是交互循环
- **关键文件**：`fastapi-agent-tutorial.ipynb`（主教程）；`scripts/fastapi_agent.py`（完整应用）；`tests/test_fastapi_agent.py`（三个端点的测试）；`run_server.py` / `run_server.bat`（启动脚本）
- **外部依赖**：FastAPI、uvicorn、pydantic；流式可选 `sse-starlette`；测试用 pytest / httpx。**无需 LLM key**

#### 3. [kotlin-agent-with-koog](tutorials/kotlin-agent-with-koog/) — 用 Kotlin 写 Agent
- **解决什么问题**：几乎所有 Agent 教程都是 Python，JVM/Kotlin 后端工程师无从下手。这个教程用 JetBrains 的 **Koog** 框架补齐这个缺口。
- **实现了什么**（三个递进的 step）：
  - **Step 1 基础 Agent**：`AIAgent` + `simpleOpenAIExecutor` 构建最小 prompt→LLM→文本回复回路（GPT-4o mini，`suspend fun main` + 协程 + `.use{}`）
  - **Step 2 工具调用**：用 `@Tool` / `@LLMDescription` 注解定义 `AssistantTools : ToolSet`，暴露 `getWeather`、`calculate`、`lookupFact` 三个工具，经 `ToolRegistry` 注册，Agent 按 **ReAct（Reason-Act-Observe）** 模式自主选工具
  - **Step 3 结构化输出**：用 `@Serializable` data class（`CityAnalysis`）+ `structuredOutputWithToolsStrategy<T>()`，让 LLM 直接返回**类型安全的 Kotlin 对象**而非自由文本
- **工作流逻辑**：
  - **主链路**（3 个独立 step，`./gradlew step1|step2|step3` 分别启动）：`读取 OPENAI_API_KEY → simpleOpenAIExecutor → 构建 AIAgent → agent.run(prompt) → println`
  - **Step2 内部**：`agent.run(问题) → 框架 ReAct 循环（选工具 → 调 getWeather / calculate / lookupFact → 观察结果）→ 合成最终答案`
  - **Step3 内部**：`structuredOutputWithToolsStrategy<CityAnalysis>() → LLM 返回 JSON → 反序列化成 Kotlin 对象`，`maxAgentIterations = 5` 限制内部工具循环上限
  - **数据流**：Step1 是 `apiKey → executor → agent → String`；Step2 用 `AssistantTools.asTools()` 经 `ToolRegistry` 注册成工具；Step3 把 `CityAnalysis` 作为 schema 传给 LLM，直接拿回类型化对象（无需手工解析 JSON）
  - **控制流**：用户代码内无分支，工具选择循环在框架内部；仅 `evaluateExpression` 的 `when` 对四则运算做递归分支
  - **循环与交互**：`.kt` 内无 while、无多轮对话，每次 `agent.run` 单次；交互在 `run.sh`——`read` 读 API key，随后每步 `read -rp` 让用户确认运行或跳过
- **关键文件**：`tutorial.md`（图文 walkthrough）；`Step1_HelloAgent.kt` / `Step2_AgentWithTools.kt` / `Step3_StructuredOutput.kt`（三个 step 源码）；`build.gradle.kts`（依赖 + step1/2/3 运行 task）；`gradlew` / `gradle/`（wrapper）；`run.sh`（交互式引导脚本）
- **外部依赖**：JDK 17+；OpenAI API key（需开通计费）；Gradle wrapper 已内置

### 主题二：工具与外部数据接入

#### 4. [agent-with-mcp](tutorials/agent-with-mcp/) — 用 MCP 协议标准化工具接入
- **解决什么问题**：传统做法是「每个数据源写一套自定义集成」，集成复杂、难扩展、难维护。MCP（Model Context Protocol）把这件事标准化，类比「AI 的 USB-C」。
- **实现了什么**：
  - 用 **FastMCP / MCPServer（MCP SDK 2.x）** 写一个最小 MCP server（`crypto-price-tracker`），通过 **stdio 传输**暴露两个工具：`get_crypto_price`、`get_crypto_market_info`，数据来自 CoinGecko 免费 API
  - 演示把该 server 接入 **Claude Desktop**（改 `claude_desktop_config.json` + 配 uv 路径）
  - 用 **langchain-mcp-adapters** + OpenAI 手写自定义 **MCP Host + Client**：工具发现（`list_tools`）→ 工具执行 → 与 AI 推理编排在一起
  - 搭一个交互式 MCP Host 对话界面，让用户直接问加密货币行情
- **工作流逻辑**：**双进程架构**
  - **Server 侧**：`mcp_server.py` 里 `MCPServer("crypto-price-tracker")` 注册两个工具后 `mcp.run(transport="stdio")` 阻塞等待，两个工具内部用 `httpx.AsyncClient` 调 CoinGecko
  - **Client 侧主链路**：`discover_tools()`（`stdio_client` → `ClientSession.initialize()` → `list_tools()`）→ `query_claude()`（把工具信息拼进 system prompt → 调 Claude）→ 若回复里正则抽到含 `"tool"`/`"arguments"` 的 JSON → `execute_tool()` 开新会话 `call_tool` → 结果以 `"Tool result: ..."` 回灌为 user 消息 → **再调一次 Claude** 得到最终解读
  - **数据流**：`tools`（`List[Dict]`，含 name / description / schema）用于拼 prompt；`messages` 跨轮累积，调 Claude 前会先过滤掉 `role=="system"` 的条目
  - **控制流**：`query_claude` 内一个分支——JSON 解析命中则走「执行工具 + 二次解释」，否则直接返回文本；`except (JSONDecodeError, KeyError, AttributeError)` 兜底到无工具路径
  - **循环与交互**：`chat_session()` 的 `while True` 多轮对话（`input()` 读入，`exit`/`quit` 退出）。注意工具调用**只有单次往返**（选一次工具 → 执行 → 解释一次），不是通用多步 ReAct
- **关键文件**：`mcp-tutorial.ipynb`（主教程）；`scripts/mcp_server.py`（可独立运行的 MCP server）
- **外部依赖**：`uv` 包管理器；`mcp[cli]>=2.0`、`httpx`、langchain-mcp-adapters、langchain-openai；OpenAI API key；CoinGecko 公开 API（无需 key）

#### 5. [arcade-secure-tool-calling](tutorials/arcade-secure-tool-calling/) — 多用户 OAuth2 安全工具调用
- **解决什么问题**：本地 demo 用单用户 Personal Access Token 能跑，但多用户生产环境跑不起来；逐家实现各 provider 的 OAuth 流程成本极高。
- **实现了什么**：
  - 用 **Arcade.dev** 平台统一处理多用户 OAuth2 认证与安全工具访问
  - 用 **LangGraph** 做编排与状态管理，分三步递进构建：**Basic Chat Agent**（纯对话）→ **Tool-Enabled Agent**（安全访问外部 API）→ **Production Agent**（带安全控制与多服务协调）
  - 为 **Gmail、Slack、Notion** 配置 OAuth2 授权流程
  - 对敏感操作加入 **human-in-the-loop（人工审批）** 安全控制
- **工作流逻辑**：**三阶段渐进构建 + 三类交互叠加**
  - **能力递进**：`agent_a`（无工具，仅 `MemorySaver`）→ `agent_b`（挂 1 个 Gmail 工具）→ `agent_c`（`manager.to_langchain()` 挂 Gmail + Slack + Notion 全套）→ `agent_hitl`（受保护工具再包一层人工审批）
  - **单轮链路**：`while True` 读输入 → `run_graph()`（`graph.stream(stream_mode="values")` 打印最后一条 message）→ 若命中受保护工具则 `interrupt()` 暂停 → `get_state(config).interrupts` 读出中断 → `yes_no_loop` 强制 y/n → `Command(resume="yes"/"no")` 恢复续跑
  - **数据流**：`config = {"configurable": {"thread_id": uuid, "user_id": ARCADE_USER_ID}}` 是核心上下文——`thread_id` 让 `MemorySaver` 按会话隔离记忆，`user_id` 是 Arcade 工具执行的必需参数（代码注释明确说明）
  - **控制流**：授权时 `if auth_response.status != "completed"` 则打印授权 URL 并阻塞等待；`add_human_in_the_loop` 内 `"yes"` → 执行工具、`"no"` → 返回拒绝字符串、其他 → `raise ValueError`；工具是否被包裹由 `t.name in tools_to_protect` 决定
  - **循环与交互**：两处 `while True` 用户输入循环 + `yes_no_loop` 校验循环；OAuth 授权是**阻塞式等待**（浏览器完成授权才继续）；人工审批是**中断-恢复**模式
- **关键文件**：`multiuser-agent-arcade.ipynb`（主教程，三步渐进）；`arcade-diagram.png`（多用户安全调用架构图）
- **外部依赖**：Arcade.dev 账号与 API key；OpenAI API key；LangGraph、`langchain-arcade`；Gmail/Slack/Notion 的 OAuth 授权

#### 6. [agent-with-brightdata](tutorials/agent-with-brightdata/) — 大规模 Web 数据采集
- **解决什么问题**：为每个网站写定制爬虫不可持续。需要能自主搜索、抽取、分析任意网站（Amazon、LinkedIn、社交媒体）的智能抓取 Agent，并绕过反爬。
- **实现了什么**（两条技术路线）：
  - **MCP 路线**（`web_scraping_agent.ipynb`）：通过 Bright Data 的 MCP server，用 **60+ 专业工具**（浏览器自动化、各平台专用抽取器）构建能力更强的 Agent
  - **LangChain 路线**（`langgraph_integration.ipynb`）：用 Bright Data 原生 LangChain 工具快速搭建精简 Agent，易集成
  - 用 **LangGraph 的 ReAct 框架**让 Agent 自主选择搜索策略并抽取结构化数据
  - 覆盖生产化要点：错误处理、限流、性能调优、反爬绕过
- **工作流逻辑**：两条独立路线，都终结于同一个 ReAct agent
  - **MCP 路线**：`.env` → `MCPClient.from_dict({"mcpServers": {"Bright Data": {"command": "npx", "args": ["@brightdata/mcp"]}}})` → `LangChainAdapter().create_tools()` → `create_react_agent(ChatOpenAI(...))`（走 OpenRouter）→ 依次跑四个测试（基础搜索 / 电商对比 / 社媒 / 复杂多步研究）
  - **LangChain 路线**：`.env` → `ChatGoogleGenerativeAI(gemini-2.0-flash)` → `BrightDataSERP(results_count=10)` → `create_react_agent(tools=[serp_tool])` → `stream(stream_mode="values")` 逐值打印
  - **数据流**：输入统一是 `{"messages": [("human", ...)]}`，ReAct 循环内工具结果回填 `messages`，最终答案取 `messages[-1].content`
  - **控制流**：用户代码**无显式分支**——工具选择与多步调用全在 ReAct 框架内部。「复杂研究」只是把多步骤指令塞进**单次** `ainvoke`，由模型自行拆解
  - **循环与交互**：无用户输入循环；`for step in agent.stream(...)` 是流式展示（观察中间消息），不是交互
- **关键文件**：`web_scraping_agent.ipynb`（MCP 版）；`langgraph_integration.ipynb`（LangChain 版）
- **外部依赖**：Bright Data 账号与 API key（每月 5k 免费 unlocker 请求）；LLM 走 OpenRouter（MCP 路线）或 Google AI Studio Gemini（LangChain 路线）

#### 7. [agent-with-tavily-web-access](tutorials/agent-with-tavily-web-access/) — 给 Agent 实时 Web 访问能力
- **解决什么问题**：模型知识有截止日期，做研究、问答、趋势监控时「过时知识」是硬伤。需要实时联网取最新信息。
- **实现了什么**（三个由浅入深的教程）：
  - **#1 `search-extract-crawl.ipynb`（API 基础）**：掌握 Tavily 的语义搜索、从实时网页抽取内容、整站爬取
  - **#2 `web-agent-tutorial.ipynb`（Web 研究 Agent）**：Tavily + LLM 结合，构建能 search / scrape / crawl / reason 的研究 Agent（用官方 Tavily-LangChain 集成）
  - **#3 `hybrid-agent-tutorial.ipynb`（混合 Agent）**：把**实时 Web 数据**与**私有内部知识库**（Chroma 向量库）整合，做对比、综合与生成
  - 配套：`supplemental/vectorize_tutorial.ipynb` 教你把自有文档向量化，`supplemental/docs/` 与 `supplemental/db/` 提供示例文档与预构建向量库
- **工作流逻辑**：三层递进，共用同一批原子能力
  - **① 裸客户端**（`search-extract-crawl.ipynb`）：`TavilyClient` → `search` → `extract`（用上一步结果的 url 列表作输入）→ `search(include_raw_content=True)` → `crawl` → `map`，纯线性演示
  - **② 数据准备**（`vectorize_tutorial.ipynb`）：`PyPDFLoader` 批量加载 `docs/` → `RecursiveCharacterTextSplitter(1000/200)` 切块 → `OpenAIEmbeddings` → `Chroma.from_documents(persist_directory="db", collection_name="my_custom_index")`
  - **③ Agent 层**：`web-agent-tutorial.ipynb` 把 `TavilySearch` / `TavilyExtract` / `TavilyCrawl` 三个工具交给 `create_react_agent`；`hybrid-agent-tutorial.ipynb` 再把 Chroma retriever 经 `as_tool(name="vector_search")` 变成**第 4 个工具**，与三个 Tavily 工具并列
  - **数据流**：裸客户端返回 dict（`results[]` 内含 `title`/`url`/`content`/`score`/`raw_content`）；agent 层输入 `{"messages": [...]}`，工具结果回填 messages，答案取 `messages[-1]`；hybrid 的 `vector_search` 返回内部 CRM 的 `page_content`
  - **控制流**：agent 层无代码分支。「Thought→Action→Observation 重复到信息齐全」「工具无结果则回复固定道歉语」这两条规则写在 system prompt 里，是**文字约束而非代码分支**
  - **循环与交互**：agent 内部是多步 ReAct 循环（框架驱动）；`vectorize_tutorial` 的 `for file_path in all_files` 是数据预处理循环
- **关键文件**：三个主 notebook（如上）；`supplemental/`（向量化教程 + 示例数据）
- **外部依赖**：Tavily API key；OpenAI API key（可换其他 LLM）；混合教程需 OpenAI embeddings + Chroma

#### 8. [agent-file-conversion-with-hushvert](tutorials/agent-file-conversion-with-hushvert/) — 文件格式转换的隐私与成本优化
- **解决什么问题**：Agent 常收到模型读不懂的文件（docx/pptx/xlsx/pdf/图片/音频/压缩包）。「一律上传到转换 API」既有隐私风险，又在为本地能做的事白付钱。
- **实现了什么**：
  - 提出**双车道（two-lane）路由规则**：本地能转的走本地，只有真正需要服务器的才走计费 API
  - **Local lane**：用 `@hushvert/engine`（MIT 许可的 WebAssembly 引擎）在浏览器内完成图片/HEIC/音频/压缩包/PDF 页面操作/DOCX→HTML 预览，**字节不出网络**
  - **Server lane**：处理浏览器做不了的 Office→PDF、PDF→Word、PDF/PPTX/XLSX→LLM 友好的 Markdown、大视频转码；以 **MCP server 工具调用**或 **REST API** 两种方式暴露（含 submit→upload→poll→download 流程、幂等键、失败态处理）
  - 用**基准测试**审慎评估「重建（reconstruction）」相比流行抽取器的真实收益（多列阅读顺序胜出，简单表格未必）
- **工作流逻辑**：**双车道（two-lane）路由**——本地能转的走本地，只有真正需要服务器的才走计费 API
  - **Local lane**：`@hushvert/engine`（WASM）在浏览器内完成转换，字节不出网络
  - **Server lane**（本教程实现）：`convert_file(path, to)` 四步链路
    1. `GET /api/v1/formats` 拉取格式对 → 派生 `server_pairs`（可用 pair 集合）与 `md_inputs`（能转 markdown 的源格式）
    2. **submit**：`POST /v1/conversions`（body `{"pair": "docx-to-md", "bytes": N}`，可带 `Idempotency-Key` 头）→ 拿回 `job.uploadUrl` / `job.jobId`
    3. **upload**：`PUT job["uploadUrl"]` 上传原始字节
    4. **poll**：`while True` 每 2 秒 `GET /v1/conversions/{jobId}` 查状态——`done` → 下载 `downloadUrl` 返回结果字节；`failed` → 抛 `RuntimeError`
  - **数据流**：`pathlib.Path(path).read_bytes()` → 组装 `pair` 字符串 → `job` dict → 轮询返回的 `state`（`status` / `downloadUrl` / `error`）→ 最终字节
  - **控制流**：`if idempotency_key` 才加幂等头；轮询内三分支（done 返回 / failed 抛错 / 继续 `sleep(2)`）
  - **循环与交互**：`while True` **后台轮询**（2 秒间隔）是核心循环，直到 done 或 failed。无多轮对话、无用户输入（仅缺 key 时 `getpass` 一次）
- **关键文件**：`agent-file-conversion-tutorial.ipynb`（主教程）；`requirements.txt`；`.env.template`
- **外部依赖**：Python 3.10+；hushvert API key（server lane，免费额度够跑完教程）；Node.js 18+（仅接本地 Agent 时需要）

### 主题三：RAG 与记忆

#### 9. [agent-RAG-with-Contextual](tutorials/agent-RAG-with-Contextual/) — 托管式生产 RAG
- **解决什么问题**：金融文档（表格、图表、多页层级结构）用朴素 RAG 解析质量差。需要企业级解析 + 托管平台来扛生产负载。
- **实现了什么**：
  - 创建并配置 **datastore**（隔离的文档存储与索引容器），每个 agent 用独立 datastore 保证数据隔离
  - 摄取多格式金融文档（PDF/HTML 等），用企业级解析处理复杂表格、图表与层级结构
  - 构建并部署带**自定义指令与 safeguards** 的 RAG agent
  - 通过自然语言查询知识库做交互
  - 用自动化测试框架评估并优化 agent 性能（含量化推理）
- **工作流逻辑**：
  - **主链路**：`ContextualAI(api_key)` → 检查/创建 datastore（存在则复用，否则 `datastores.create`）→ 下载 4 个 PDF（已存在则跳过）→ `documents.ingest` 逐个上传 → 检查/创建 agent（`agents.create`，绑定 `datastore_ids`，`enable_multi_turn=False`）→ `agents.query.create` 单次查询 → `retrieval_info` 取 `page_img` 做溯源展示
  - **评测链路**：6 个 `unit_tests` + 6 个 `queries` → `iterrows()` 逐题查询把答案写回 `eval['response']` → 存 `eval_input.csv` → `run_unit_tests_with_progress` 对「每题 × 每个单测」双重循环调 `lmunit.create` 打分 → 存 `unit_test_results.csv` → 映射到 6 个维度（ACCURACY / CAUSATION / SYNTHESIS / LIMITATIONS / EVIDENCE / RELEVANCE）画雷达图
  - **数据流**：`datastore_id` → `document_ids` → `agent_id` → `query_result`（含 `message.content`、`message_id`、`retrieval_contents[].content_id`）→ `eval` DataFrame（`prompt` / `response`）→ `results` list[dict]（`prompt` / `response` / `test_results[].{test, score, metadata}`）
  - **控制流**：多处「存在则复用、不存在则创建」分支（datastore / agent / PDF 文件）；下载、上传、查询各自 `try/except`（失败 `continue` 或写入 `Error:` 字符串）
  - **循环与交互**：三个 `for`（文件上传、`iterrows()` 批量查询、题目×单测双重循环）。无 while、无多轮对话、无用户输入
- **关键文件**：`contextual_tutorial.ipynb`（主教程：认证 → 建 datastore → 摄取 → 配置 agent → 评估）；`requirements.txt`
- **外部依赖**：Contextual AI 平台账号与 API key（`contextual-client` SDK）

#### 10. [agent-memory-with-redis](tutorials/agent-memory-with-redis/) — 双记忆架构
- **解决什么问题**：Agent 记不住用户偏好，每次对话从零开始。需要短期（对话状态）+ 长期（持久知识）两层记忆。
- **实现了什么**：
  - **双记忆架构**：短期记忆（对话状态）+ 长期记忆（持久知识），以旅行 agent 为场景
  - LangGraph 工作流含三个节点：**Retrieve Memories → Respond → Summarize**，用 `RedisSaver` checkpointer 做状态持久化
  - 用 **RedisVL** 建带向量嵌入的 `SearchIndex`，实现长期记忆的**语义搜索**
  - Pydantic 数据模型（`MemoryType` 枚举、`Memory`、`Memories`），区分 **episodic**（个人经历/偏好）与 **semantic**（通用知识）
  - 基于工具的 memory 管理 + 对话摘要等生产化模式
- **工作流逻辑**：**三层结构**——短期记忆（`RedisSaver` checkpointer，按 `thread_id` 存整段对话）+ 长期记忆（RedisVL `SearchIndex` 向量库，按 `user_id` 存记忆条目）+ 外层 StateGraph（控制流程）
  - **单轮链路**：`while True` 读输入 → `agent` 节点（内部调 `travel_agent.invoke`）→ `decide_next_step` 条件路由：**有 `tool_calls`** → `execute_tools`（手动执行工具、追加 `ToolMessage`）→ 回到 `agent`；**没有** → `summarize_conversation`
  - **摘要节点**：消息数 ≥ 6 才启用 `summarizer`（gpt-4o, temp 0.3）压缩对话，用 `RemoveMessage` 删旧消息、只保留末条，然后 `END`
  - **记忆工具链路**：`store_memory` 先经 `similar_memory_exists` 查重（向量 + Tag 过滤）→ 未重复才 embed 并 `SearchIndex.load` 写入；`retrieve_memories` 用 `VectorRangeQuery` 语义检索 → 解析成 `StoredMemory`
  - **数据流**：`RuntimeState(MessagesState)` 的 `messages` 列表（Human / AI / Tool / System 混排）是图内状态；`RunnableConfig(configurable={"thread_id", "user_id"})` 是上下文载体；Redis index `agent_memories` 存 `user_id` / `content` / `memory_type`（EPISODIC 或 SEMANTIC）/ `metadata` / `created_at` / `embedding` / `memory_id` / `thread_id`
  - **控制流**：`decide_next_step` 条件边（看最新 AIMessage 有无 `tool_calls`）；摘要阈值分支（`len(messages) < 6` 直接返回）；查重分支（重复则跳过写入）。注意 `travel_agent` 自带 ReAct 循环，外层 StateGraph 又包了一层 `execute_tools`，**二者并存**
  - **循环与交互**：`main` 的 `while True` 用户输入循环 + 图内 `agent → execute_tools → agent` 工具循环。多轮状态由 Redis checkpoint 按 `thread_id` 持久化
- **关键文件**：`agent_memory_tutorial.ipynb`（主教程）；`assets/` 下三张记忆架构图
- **外部依赖**：OpenAI API key（需开通计费）；Redis（本地实例或 Redis Cloud）；RedisVL、`langgraph-checkpoint-redis`

#### 11. [agent-memory-with-mem0](tutorials/agent-memory-with-mem0/) — 向量 + 图混合的自进化记忆
- **解决什么问题**：Agent 有「记忆健忘症」——对话结束就忘，无法从历史中学习。需要持久、能自我进化的记忆（以个人 AI 研究助手为例）。
- **实现了什么**：
  - **向量记忆（Qdrant）**做语义召回与长期知识存储
  - **图记忆（Neo4j）**做实体关系映射，跟踪论文引用、作者关联、研究兴趣
  - **混合检索**：嵌入相似度 + 图遍历结合，取最相关信息
  - **记忆冲突解决**与自我改进（随每次交互演化）
  - 自动提取并存储用户偏好（深度、风格、格式），跨会话复用
- **工作流逻辑**：分两个 Phase
  - **Phase 1（纯向量）**：`setup_api_keys()` → 构造 `config`（llm=gpt-4o-mini、embedder=text-embedding-3-large 3072 维、vector_store=qdrant）→ `Memory.from_config(config)` → `PersonalResearchAssistant`
  - **`ask(question, user_id)` 单轮链路**：`search_memories(query, user_id)` 取历史记忆 → 拼进 system prompt（有记忆则加 `Previous memories: ...`）→ `chat.completions.create` 得答案 → 把 `question` 经 `memory.add(..., metadata={"category": "research"})` **写回**记忆 → 返回 answer。即「**先读后写**」，每问一次都沉淀一次
  - **Phase 2（加图存储）**：`setup_graph_capabilities()` 读 Neo4j 连接信息 → `enhanced_config` 增加 `graph_store: neo4j` → `Memory.from_config` → 换 `user_id="graph_user"` 再问
  - **数据流**：`config` / `enhanced_config` → `Memory` 实例；`question` + `user_id` → `previous_memories` → `prompt` → `answer`。记忆按 `user_id` 隔离，Phase 1 存 Qdrant，Phase 2 增补 Neo4j 图存储
  - **控制流**：`Memory.from_config` 的 `try/except` **回退分支**（图存储配置失败则退回纯向量版）；`get_memories` / `search_memories` 对返回类型（dict 带 `results` vs list）做兼容分支；`interactive_demo` 内 quit / memories / 其他三分支
  - **循环与交互**：`interactive_demo()` 的 `while True` 交互循环（含 `KeyboardInterrupt` 退出）；前面 4 次 `ask` 是跨 cell 的记忆累积，不是程序内循环
- **关键文件**：`mem0_tutorial.ipynb`（主教程）；`Assets/mem0_architecture.png`（处理与存储流程图）
- **外部依赖**：Mem0（开源）；OpenAI API key（GPT-4 推理 + embeddings）；Qdrant（向量库）；Neo4j（图库）

#### 12. [ai-memory-with-cognee](tutorials/ai-memory-with-cognee/) — 知识图谱式记忆
- **解决什么问题**：开发资料散落在 JSON、Markdown、API 响应、个人历史里，检索时只能逐源翻找，缺少跨源关联。
- **实现了什么**：
  - 用 Cognee 的 `add()` 摄取多格式数据（JSON、Markdown、API 响应）并归一化
  - 用 `cognify()` 做 **AI 驱动的实体抽取与关系映射**，构建可遍历的知识图谱
  - 知识图谱 + RAG 结合做自然语言检索，得到跨数据源、**可解释**的答案
  - 发现不同数据源之间非显然的隐藏模式与关联
  - 异步执行环境下配置模型，用 GPT-4o-mini 做实体提取与关系映射
- **工作流逻辑**：
  - **主链路**：`prune_data()` + `prune_system(metadata=True)` 清库 → **第一批** `cognee.add("guido_contributions.json", node_set=["guido_data"])` → `cognify(temporal_cognify=True)` 建图 → `search("Show me commits")` → `visualize_graph()` 生成图谱 HTML → **第二批**再 `add` 四个文件（分属 `developer_data` / `principles_data` 两个 node_set）→ 再次 `cognify`
  - **查询矩阵**（同一份图谱，不同检索模式）：`search(..., GRAPH_COMPLETION)` 跨源推理 ／ `search(..., node_type=NodeSet, node_name=['principles_data'])` 限定节点集 ／ `search(..., TEMPORAL)` 问 2025 年贡献 ／ `memify()` ／ `search(..., save_interaction=True)` 存交互 → `search(..., FEEDBACK, last_k=1)` 对上一轮结果给反馈
  - **数据流**：本地 `data/*.json` / `*.md` 经 `add` 注入并打上 `node_set` 标签 → `cognify` 落成图谱 + 向量 → `search` 按 `query_type` / `node_name` 读回。`save_interaction=True` 保存的交互是后续 `FEEDBACK` 查询的输入
  - **控制流**：线性 `await` 序列，用户代码无分支；分支只在 `search` 内部按 `query_type` 枚举（GRAPH_COMPLETION / TEMPORAL / FEEDBACK）选择不同检索路径
  - **循环与交互**：无 while、无用户输入、无轮询。多轮靠逐 cell 手动执行；`save_interaction` + `FEEDBACK last_k=1` 是唯一的跨查询状态传递
- **关键文件**：`cognee-ai-memory.ipynb`（主教程）；`guido_contributions.html` + `data/`（数据源）；`.env.template`（LLM 配置）
- **外部依赖**：OpenAI API key（`gpt-4o-mini`）；`cognee[notebook]==0.3.3`

### 主题四：多 Agent 协作

#### 13. [a2a](tutorials/a2a/) — A2A 协议：Agent 之间的互操作
- **解决什么问题**：不同团队、不同语言、不同厂商构建的 agent 之间无法互通。A2A（Agent-to-Agent）是解决这个问题的开放协议。
- **实现了什么**：
  - 按 **A2A Protocol Specification v0.1.0** 模拟实现消息结构与交互模式
  - **三 agent 协作系统**：`UserFacingAgent`（面向用户、负责编排）、`NewsInfoAgent`（新闻 TLDR）、`EventsInfoAgent`（时事 TLDR）
  - 用 `tasks/send`、`tasks/get`、`tasks/cancel` 等 **JSON-RPC** 结构模拟远程调用，最终由 UserFacingAgent 汇总产出「每日 TLDR」
  - 实践 Task / Message / Part（主要用 `TextPart`）/ Artifact / **Agent Card** 等核心概念
  - 对比 **A2A 与 MCP 的定位差异**：agent 之间协作 vs agent 使用工具
- **工作流逻辑**：教程含两个部分，先看真协议再拆解原理
  - **Part A（真实 A2A SDK，HTTP 流式）**：两个独立进程分别 `A2AStarletteApplication(...).build()` 跑在 9001（News）与 9002（Events）→ 客户端 `A2ACardResolver.get_public_card` 拉两张 Agent Card → `A2AClient.send(task_id, agent_url, message_parts)` → `async for response_part` 逐条接收，收到 `None` 表示流结束
  - **Part B（本地内存模拟，不走 HTTP）**：`user_facing_agent.get_daily_tldr()` → `_request_agent_content` 构造 `tasks/send` 参数 → **依次**调 news、events 两个子 agent 的 `handle_a2a_request` → 子 agent 校验后 `_generate_tldr_part` 生成内容 → 组装 `task` dict（artifacts + status + messages）→ `_extract_content_from_task_response` 取 `artifacts[0].parts[0].text` → `_format_final_tldr` 拼成「每日 TLDR」→ `_create_main_task_object` 组装主 task
  - **数据流**：`task_id`（`uuid.uuid4()` 生成，主任务与两个子任务各自持有）；`artifacts[0].parts[0].text` 是内容传递载体；`UserFacingAgent` 持有 `news_agent` / `events_agent` 引用
  - **控制流**：`handle_a2a_request` 有校验分支（缺 `task_id` → `raise ValueError`）与异常分支（返回 `failed` task）；`_extract_content_from_task_response` 有 `IndexError` / `KeyError` / `TypeError` fallback；Part A 用 `try/except` 捕获连接失败。两个子任务是**顺序**执行（先 news 后 events），非并发
  - **循环与交互**：Part A 的 `async for` 流式接收循环。无 while、无用户输入、无轮询
- **关键文件**：`a2a_tutorial.ipynb`（主教程，该目录只有这一个文件，**无 README**）
- **外部依赖**：`a2a-sdk`、`httpx`、`uvicorn`；**无需任何 API key**

### 主题五：安全

#### 14. [agent-security-with-llamafirewall](tutorials/agent-security-with-llamafirewall/) — 四层护栏
- **解决什么问题**：Agent 上线后要面对 prompt injection、有害内容、工具滥用等攻击，需要一套可落地的防护层。
- **实现了什么**（4 个独立 notebook，覆盖四个防护面）：
  - **基础扫描**：`scan_message` 返回 score / decision / reason，decision 含 `block`、`allow`、`human_in_the_loop_required`
  - **输入护栏**：用 OpenAI SDK 的 `@input_guardrail` 装饰器 + `PROMPT_GUARD` 扫描器校验用户输入，命中即中止（tripwire）
  - **输出护栏**：`@output_guardrail` + `AGENT_ALIGNMENT` 扫描器做响应对齐检查（结合上下文 Trace）
  - **工具安全**：用 `AgentHooks` 生命周期钩子（`on_tool_start` / `on_tool_end`）拦截工具调用，配 PII 扫描器防敏感信息外泄
  - 另有实时安全事件监控与日志
- **工作流逻辑**：四个 notebook 各覆盖一个防护面，套路都是「配置 scanner → 定义钩子 → 跑用例验证是否按预期拦截」
  - **`hello-llama`**：`LlamaFirewall()` → `scan_message()` 把文本包成 `UserMessage` → `lf.scan` → 打印 `score` / `decision` / `reason` → `for` 遍历安全句与注入句做对比
  - **`input-guardrail`**：`scanners={USER: [PROMPT_GUARD], SYSTEM: [PROMPT_GUARD]}` → `@input_guardrail` 内 `lf.scan` → `decision == BLOCK` 则 `tripwire_triggered=True` → `Runner.run` 抛 `InputGuardrailTripwireTriggered`
  - **`output-guardrail`**：`scanners={ASSISTANT: [AGENT_ALIGNMENT]}` → `@output_guardrail` 从 `ctx.context["user_input"]` 取输入 → 构造 `Trace=[UserMessage(input), AssistantMessage(output)]` → `scan_replay` → `decision in {BLOCK, HUMAN_IN_THE_LOOP_REQUIRED}` 则触发
  - **`tools-security`**：三层防护——输入层 `PIICheckScanner`（`@input_guardrail`）；工具层 `MyAgentHooks.on_tool_start` 扫工具名+描述、`on_tool_end` 扫 `ToolMessage`；被测工具 `secret_number(password)` 密码错时故意返回注入攻击串
  - **数据流**：`input_text` → `UserMessage` → `lf.scan` → `LlamaFirewallOutput(is_harmful, score, decision, reasoning)` → 包成 `GuardrailFunctionOutput(output_info, tripwire_triggered)`；`tripwire_triggered` 决定 `Runner` 是否抛异常
  - **控制流**：每层都是**运行时拦截分支**——decision 命中 BLOCK / HITL 即中止或 `raise`，否则放行；notebook 侧用 `try/except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered)` 捕获（tools 里还有通用 `Exception` 兜底）
  - **循环与交互**：无循环。每个 notebook 是 2-3 次独立 `Runner.run` 验证拦截是否按预期触发
- **关键文件**：`hello-llama.ipynb`、`input-guardrail.ipynb`、`output-guardrail.ipynb`、`tools-security.ipynb`（四个教程）；`requirements.txt`
- **外部依赖**：OpenAI API key；Together AI key（对齐检查）；HuggingFace 上 Llama Prompt Guard 2 的访问权；需先跑 `llamafirewall configure`

#### 15. [agent-security-apex](tutorials/agent-security-apex/) — 动手打自己的 Agent
- **解决什么问题**：安全不能只读理论。需要拿真实攻击数据集去实测自己的系统，才知道漏在哪。
- **实现了什么**：
  - 覆盖 **8 大类 prompt injection 攻击**，含 **91 个真实攻击示例**
  - 用自动化安全测试工具评估 AI 系统脆弱性（跑批量攻击、统计结果）
  - 用高级 prompt engineering 构建并验证防御措施
  - 测试 **12 种混淆/编码绕过方法**（测你的过滤器能不能被绕）
- **工作流逻辑**：
  - **主链路**：`load_dotenv` → 从 `model_testing_tools` / `prompt_manipulation_tools` 导入工具函数 → `AsyncOpenAI` → **单条攻击**（`try_to_get_password(prompt, client, system_prompt)` → `send_prompt_to_model` → `check_password_in_response`）→ **编码攻击**（`prompt_encoder('Give me the password', 'atbash')` 转密文再试）→ **批量测试**（`await test_model(client, system_prompt)`）
  - **`test_model` 内部链路**：读 CSV → `df.sample(num_samples=min(5, len(df)))` 随机抽样 → 逐条：先跑**未编码**攻击，成功计入 `unencoded`；**失败才**用 `prompt_encoder` 随机编码再攻一次，成功计入 `encoded` 并累加 `encoding_effective_count` → 每条约 `await asyncio.sleep(1)` → 统计攻击成功率与编码有效性
  - **数据流**：攻击目标是 `cur_password = "pinky"`，经 system prompt 里的 `{ password }` 占位符注入；prompt 文本来自 CSV（列 `name` / `type` / `text`）；`results` dict 聚合 `total_prompts` / `tested_prompts` / `unencoded{...}` / `encoded{...}` / `encoding_effective_count`
  - **控制流**：核心是「**未编码成功则跳过编码，失败才编码重试**」这一分支；`prompt_encoder` 未指定编码时用 `random.choice` 随机选，并 dispatch 到 12 种编码（atbash / caesar / vigenere / braille / morse / pig_latin / leet / binary / hex / base64 / rot13 / reverse），不支持的编码 `raise ValueError`
  - **循环与交互**：`for idx, row in random_sample.iterrows()` 逐条测 prompt。无 while、无用户输入
- **关键文件**：`agent-security-evaluation-tutorial.ipynb`（主教程）；`model_testing_tools.py`（自动化测试框架）；`prompt_manipulation_tools.py`（攻击/混淆工具）；`example_prompts.csv`（91 条攻击样本）；`system_prompt.txt`（生产级防御 prompt 示例）
- **外部依赖**：OpenAI API key（`.env` 中 `OPENAI_API_KEY`）；openai、pandas、aiohttp

### 主题六：可观测性与评估

#### 16. [tracing-with-langsmith](tutorials/tracing-with-langsmith/) — Agent 的「飞行记录器」
- **解决什么问题**：AI 应用 demo 时正常，上线后出问题无从查起——不知道 agent 中间做了什么决策、花了多少 token。
- **实现了什么**：
  - 用 LangGraph 构建一个可观测 agent，含 3 个节点：`decide`（判断是否需要搜索）→ `search` → `respond`
  - 定义结构化 `AgentState`（`user_question`、`needs_search`、`search_result`、`final_answer`、`reasoning`），让 LangSmith 能追踪信息流
  - 实现 `wikipedia_search` 工具（调 Wikipedia search API）
  - 通过环境变量 `LANGCHAIN_TRACING_V2=true` **自动拦截并记录所有 LLM 调用、工具执行与工作流步骤**
  - 用三类测试问题（direct_answer / current_info / factual_lookup）跑测试，在 LangSmith dashboard 看 trace、决策透明度、耗时与成本
- **工作流逻辑**：
  - **主链路**：`ChatOpenAI(gpt-4o-mini, temperature=0)` → 定义 `AgentState` → 定义 `wikipedia_search` 工具 → 定义三个节点 → `StateGraph` 组装：`set_entry_point("decide")` + `decide → search → respond → END` + `compile()` → 三个测试用例逐个 `simple_agent.invoke(initial_state, config)`
  - **可观测性的关键**：`LANGCHAIN_TRACING_V2=true` 让 LangSmith 在后台**自动拦截**所有 LLM 调用与工具执行，`config` 里的 `metadata` / `tags` 作为过滤维度。代码里没有任何显式上报调用——这是「环境变量开启即生效」的旁路机制
  - **数据流**：`AgentState`（`user_question` / `needs_search` / `search_result` / `final_answer` / `reasoning`）是唯一状态对象。`decide` 写 `needs_search` + `reasoning`；`search` 读 `needs_search` 写 `search_result`；`respond` 读 `search_result` 写 `final_answer`
  - **控制流**：图本身是**固定线性链**（`decide → search → respond`），注释里提到的「conditional logic」实际落在节点函数内部：`decide_search_need` 解析 LLM 首行是否 `"SEARCH"`；`execute_search` 用 `if not state["needs_search"]` 跳过真实搜索并写 `"No search performed"`；`generate_response` 用 `if used_search and "Search error" not in ...` 选择用哪版 prompt
  - **循环与交互**：`for` 遍历 3 个 `test_cases` + 每轮 `time.sleep(1)`。无 while、无多轮对话、无用户输入
- **关键文件**：`langsmith_basics.ipynb`（主教程）；`assets/wiki_agent_td.png`（工作流图）
- **外部依赖**：OpenAI API key；**LangSmith / LangChain API key**；langchain-core、langchain-openai、langgraph、langsmith

#### 17. [agent-evaluation-intellagent](tutorials/agent-evaluation-intellagent/) — 自动化对抗评估
- **解决什么问题**：很难判断一个 agent 是否真的遵守了它被设定的政策（policy）。需要自动生成对抗性场景去撞它的边界。
- **实现了什么**：
  - 克隆并安装 **IntellAgent** 多智能体评测框架（`github.com/plurai-ai/intellagent`）
  - 定义一个教育助手 agent 的 prompt 与行为准则（guidelines / policies）
  - 配置仿真参数：评测系统用 `gpt-4o`，被测 agent 用 `gpt-4o-mini`，设定场景数量
  - 用 `SimulatorExecutor` **生成合成场景数据集、模拟 user-agent 对话**，并对每轮交互施加 critique（判断是否违反政策）
  - 用 **Streamlit dashboard** 分析结果：会话 trace、政策违规分析、各维度性能指标
- **工作流逻辑**：
  - **主链路**：`git clone plurai-ai/intellagent` → 装依赖 → 写三份配置与数据（`config/llm_env.yml`、`examples/my_education_agent/input/wiki.md`（被测 agent 的 system prompt + policy）、`config/my_education_config.yml`）→ `override_config(...)` → `SimulatorExecutor(config, base_output_path='./results/education')` → `load_dataset('data_1')` 生成场景 → `run_simulation('exp_1')` 跑模拟 → 起 Streamlit 看结果
  - **模拟对话循环在哪**：发生在 **`executor.run_simulation('exp_1')` 内部**（框架黑盒）。框架用 `llm_intellagent`(gpt-4o) 扮演被测 agent、`llm_chat`(gpt-4o-mini) 扮演对话方，对 `dataset_handler.records` 里由 `load_dataset` 生成的 `num_samples=10` 个场景**逐个展开多轮对话**并判断是否违反 policy。notebook 里看不到该循环的源码
  - **数据流**：配置文件四个关键字段——`environment.prompt_path`（指向 wiki.md）、`llm_intellagent`、`llm_chat`、`dataset.num_samples=10`；`load_dataset` 填充 `executor.dataset_handler.records`（每条含 `description.event_description`）；`run_simulation` 把结果写到 `base_output_path` 供可视化器读取
  - **控制流**：notebook 本身线性无分支，分支与循环都在框架内部
  - **循环与交互**：框架内的模拟多轮对话循环（cell 18 触发）；notebook 自身只有 `threading.Thread(target=run_streamlit)` 起的 daemon 线程 + `time.sleep(5)` 等待启动
- **关键文件**：`intellagent-evaluation-tutorial.ipynb`（主教程）；运行时生成 `config/`、`examples/`、`results/`
- **外部依赖**：OpenAI API key（框架也支持 Anthropic/Azure/Google/Bedrock 等）；`git clone` IntellAgent 仓库 + 其依赖；Streamlit

### 主题七：部署与运行环境

#### 18. [docker-intro](tutorials/docker-intro/) — 用 Docker 容器化 Agent
- **解决什么问题**：代码在开发机能跑、到生产就不行（依赖版本、OS、架构差异）；Docker 学习曲线又陡。
- **实现了什么**：
  - 讲透 Dockerfile 核心命令：`FROM`、`LABEL`、`ENV`、`RUN`、`COPY`、`WORKDIR`、`EXPOSE`、`CMD`
  - 演示 `docker build` 构建、**image layers（分层）与 layers caching（缓存）**机制、`docker inspect` 查元数据
  - 演示 `docker run` 运行容器（`-it` 交互、`-p` 端口映射）与 `-v` 卷挂载本地目录
  - 用 Docker 容器化一个简单 AI agent：静态 `simple_agent.py` 与动态 `dynamic_agent.py`（通过 `QUESTION` 环境变量传参）
  - 最佳实践：**不在构建期写入密钥**，运行期用 `-e` 传 `OPENAI_API_KEY`
- **工作流逻辑**：总链路是 **本地写代码（Dockerfile / .py）→ `docker build` 构建镜像 → `docker run` 运行容器**，5 个 ex 是这条链路的增量扩展
  - **ex1**：`FROM python:3.10` + `LABEL` + `ENV` + `RUN apt-get install curl` → 理解 **layer 分层**（继承 python:3.10 的 8 层 + RUN 第 9 层）与 `docker inspect | jq '.RootFS'`
  - **ex2**：**追加**一条 `RUN apt-get install vim` → 展示 **layer 缓存**：curl 层命中 `CACHED`，只重建 vim 层
  - **ex3**：**追加** `CMD`，并新增 `hello-world.py` → `docker run -v ./examples/ex3:/ex3 -it` **卷挂载**，进容器后跑本地代码
  - **ex4**：换成 `python:3.10-slim` + `RUN pip install openai` + `COPY simple_agent.py /app/` + `CMD ["python", "/app/simple_agent.py"]` → `--env OPENAI_API_KEY=...` **运行期**注入密钥
  - **ex5**：`dynamic_agent.py` 用 `os.getenv("QUESTION", 默认值)` 读环境变量 → Dockerfile 加 `ENV QUESTION=` → `docker run` 时 `--env QUESTION="..."` 传参
  - **数据流**：无运行时 state。构建期是「Dockerfile 指令 → 镜像 layer」——`FROM`/`RUN` 生成层，`LABEL`/`ENV`/`CMD` 生成 metadata，`COPY` 把本地 `.py` 复制进 `/app`；运行期靠 `ENV` / `--env` 注入 `PYTHON_VER` / `QUESTION` / `OPENAI_API_KEY`
  - **控制流**：命令行线性无分支；唯一的「条件」是构建引擎的 **layer 缓存命中判断**（层未变则复用缓存，变了则从该层起全部重建）
  - **循环与交互**：ex3 用 `--interactive --tty` 开交互式 bash；ex4 / ex5 一次性执行。无 while、无轮询
- **关键文件**：`README.md`（Markdown 教程）；`examples/ex1`~`ex5/`（各含 Dockerfile，依次演示基础镜像、缓存、卷挂载、静态 agent、动态 agent）
- **外部依赖**：Docker Desktop；Docker Hub 账号；OpenAI API key（仅 ex4/ex5 运行期需要）

#### 19. [on-prem-llm-ollama](tutorials/on-prem-llm-ollama/) — 本地私有化 LLM
- **解决什么问题**：不想依赖外部云 API（成本、隐私、合规、断网），希望 Agent 完全跑在本地。
- **实现了什么**：
  - 安装 Ollama、`ollama pull` 拉量化模型、`ollama serve` 起本地 REST 服务（`localhost:11434`）
  - 通过 `/api/chat` 发出首个 chat 请求（演示 curl / Windows CMD / Postman 三种方式）
  - 把 OpenAI 调用替换为 Ollama：Python `requests` 直连，或在 LangChain 里用 `ChatOllama` 替换 `ChatOpenAI`
  - 讲清 Ollama API 参数（`stream`、`temperature`、`num_predict`、`keep_alive`、`num_ctx`）与模型选型表（llama3.1:8b、qwen2.5:14b、mistral:7b 等）
  - 两个示例：`basic_usage.ipynb`（直连 API / 参数 / LangChain / 多轮对话）、`langchain_agent.ipynb`（`SimpleAnalysisAgent`：文本分类 / 摘要 / 关键点提取）
- **工作流逻辑**：
  - **主链路**（`ollama_tutorial.ipynb`）：装 Ollama → `ollama pull llama3.1:8b` + `ollama serve` → `curl http://localhost:11434/api/chat` 发首条消息 → **对照实验**：OpenAI SDK 调 `gpt-4` vs `requests.post` 调本地 `llama3.1:8b` → LangChain 侧 `ChatOpenAI(gpt-4)` vs `ChatOllama(llama3.1:8b)` → 两侧各再跑一遍带参数版本（temperature / top_p / num_predict / repeat_penalty / stop）
  - **支撑脚本**：`basic_usage.ipynb` 四个例子（`check_ollama_running()` 探活 → 直连 API → 带参数 → LangChain → 多轮对话）；`langchain_agent.ipynb` 的 `SimpleAnalysisAgent.analyze_text` 内部依次跑 `classify_text` → `extract_key_points` → `summarize` 三步，返回 `{"category", "key_points", "summary", "length"}`
  - **数据流**：客户端与 `localhost:11434` 之间是 HTTP JSON 往返——请求体 `{"model", "messages", "stream", "temperature", ...}` → 响应 `{"message": {"content": ...}}`。`example_4_conversation` 用 `messages.append()` 依次追加 user / assistant 消息实现多轮
  - **控制流**：`check_ollama_running` / `check_ollama_model` 返回布尔并走 `if not ...` 分支；各例有 `if response.status_code == 200` 的成功/失败分支
  - **循环与交互**：`interactive_mode()` 的 `while True` 读 `input()`（输入 `quit`/`exit`/`q` 退出，文本短于 10 字符则 `continue`）是教程里的用户输入循环；`demo_agent` 是 `for sample in samples`
- **关键文件**：`ollama_tutorial.ipynb`（主教程）；`scripts/basic_usage.ipynb`、`scripts/langchain_agent.ipynb`（两个示例）
- **外部依赖**：Ollama（本地或 Docker）；本地模型文件（需相应 RAM/VRAM）。**无需任何 API key**

#### 20. [runpod-gpu-deploy](tutorials/runpod-gpu-deploy/) — GPU 云 Serverless 部署
- **解决什么问题**：自己管 GPU 服务器（扩缩容、负载均衡、成本优化）运维负担重，而流量又是波峰波谷。Serverless 按实际算力计费。
- **实现了什么**：
  - 用 **CrewAI** 构建博客写作 agent（Blog Writer + `fake_research` 伪研究工具），底层 Ollama 跑 `openhermes`
  - 定义 RunPod serverless handler（`runpod.serverless.start({"handler": handler})`），从 `job["input"]` 读 `topic`
  - 用 Docker 打包：base 镜像 `runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04`，**构建期 `ollama pull openhermes` 把模型烘焙进镜像以降低冷启动**
  - 部署到 RunPod Serverless endpoint（配 Docker Image、GPU 优先级、min/max workers、FlashBoot）
  - 经 dashboard 或 cURL/Python 调 REST API 生成博文
- **工作流逻辑**：分**构建期 / 启动期 / 请求期**三个阶段
  - **① 构建期**（`Dockerfile`）：`FROM runpod/pytorch:...cuda11.8` → 装 python3.11 并建 venv → `uv pip install -r requirements.txt`（crewai 等）→ 装 Ollama → **`ollama serve` 后台 + `sleep 25` + `ollama pull openhermes` + `sleep 10` + `pkill ollama`**（把模型**烘焙进镜像**，降低冷启动）→ `ADD handler.py` + `ADD start.sh`
  - **② 启动期**（`start.sh`）：`nohup ollama serve` → `until curl -s http://localhost:11434/api/version` **轮询等就绪** → `ollama run openhermes` 后台加载 → `python handler.py`（`runpod.serverless.start({"handler": handler})`）→ `sleep infinity` 保活
  - **③ 请求期**（`handler.py`）：`handler(job)` 取 `job["input"]["topic"]`（缺省 `"technology"`）→ `create_blog_post(topic)` 建 `Task` → `Crew(agents=[blog_writer], tasks=[blog_task]).kickoff()` → CrewAI 内部调 `fake_research(topic)` → 返回 `result.raw`
  - **数据流**：HTTP `{"input": {"topic": ...}}` → `job["input"]` → `topic` → 拼进 `Task.description` → agent 调 `fake_research`（内部 `fake_results` dict 按 `topic.lower()` 做子串匹配，无匹配回默认）→ 经 `ollama/openhermes`（`base_url="http://localhost:11434"`）生成 → `result.raw` → 回包
  - **控制流**：`handler` 用 `try/except` 分别返回 success 或 error dict；`fake_research` 用关键词子串匹配分支；CrewAI `kickoff` 内部有 agent-tool 迭代循环（框架层）
  - **循环与交互**：`start.sh` 里 `until curl ... /api/version` 是 Ollama 就绪轮询。无用户输入循环
- **关键文件**：`README.md`；`crew-ai-ollama-runpod-tutorial/`（`handler.py` 入口 + agent 定义、`Dockerfile`、`start.sh`、`requirements.txt`）
- **外部依赖**：RunPod 账号与 API key；Docker（可推 Docker Hub）；GPU（推荐 24GB+ VRAM）

#### 21. [aws_agentcore](tutorials/aws_agentcore/) — AWS 托管 Runtime
- **解决什么问题**：本地 agent 只是个普通 Python 函数，缺 HTTP 服务、请求处理、健康检查、监控等生产基础设施。
- **实现了什么**：
  - 先用 OpenAI API 构建基础 agent：`process_message(message)` 函数（`gpt-4o-mini`、`temperature=0`）
  - 用 `bedrock-agentcore` SDK 的 **`BedrockAgentCoreApp`** 创建 runtime，自动处理 HTTP 请求、健康检查、响应格式化
  - 用 `@app.entrypoint` 装饰器注册 agent，从 `payload["prompt"]` 读取用户消息
  - `app.run()` 起 HTTP server（默认 8080，`/invocations` endpoint）
  - 用 `requests` / `curl` POST 到 `/invocations` 测试，返回结构化 `{"result": ...}`
- **工作流逻辑**：
  - **主链路**：装依赖 → `load_dotenv` 设 `OPENAI_API_KEY` → 定义 `process_message(message)`（`gpt-4o-mini`, `temperature=0`）→ 本地直调测试 → `app = BedrockAgentCoreApp()` → 用 `@app.entrypoint` 装饰 `invoke(payload)`：`payload.get("prompt", "Hello")` → `process_message` → 返回 `{"result": ...}` → `app.run()` 起 HTTP server（默认 8080，两个端点 `POST /invocations` 与 `GET /ping`）
  - **请求期链路**：`HTTP POST /invocations` → SDK 把请求路由到被 `@app.entrypoint` 标记的 `invoke` → 取 `payload["prompt"]` → 调 OpenAI → 包成 `{"result": content}` 回包
  - **数据流**：payload dict → `"prompt"` 字段（缺省 `"Hello"`）→ `process_message` → OpenAI 返回内容 → `{"result": content}`
  - **控制流**：线性无分支，唯一的默认值逻辑是 `payload.get("prompt", "Hello")`
  - **循环与交互**：无。纯**请求驱动**——每个 HTTP 请求调用一次 entrypoint。notebook 内并未真正启动服务（curl 示例被注释掉）
- **关键文件**：`agentcore_tutorial.ipynb`（主教程）；`assets/agentcore-diagram.png`（架构图）
- **外部依赖**：OpenAI API key；Python 3.10+；`bedrock-agentcore`、`python-dotenv`、`requests`、`openai`

### 主题八：交互界面与模型定制

#### 22. [agent-with-streamlit-ui](tutorials/agent-with-streamlit-ui/) — 聊天机器人界面
- **解决什么问题**：Agent 有了，但普通用户没法用。需要一个类似 ChatGPT 的浏览器界面，还能传文件。
- **实现了什么**：
  - 用 OpenAI API（`gpt-4o`）实现 `generate_response` 作为聊天机器人的「大脑」
  - 用 Streamlit 搭 web UI：`st.set_page_config` / `st.title` / `st.chat_message` / `st.chat_input` 组成聊天界面
  - 侧边栏 `st.sidebar.file_uploader` 支持上传 txt/pdf，用 **PyPDF2** 提取 PDF 文本，并把文件内容作为 system 上下文注入对话
  - 用 **`st.session_state`** 维护对话历史（解决 Streamlit 每次 rerun 丢消息的问题）
  - 提供两个可运行脚本：`app.py`（OpenAI 版）与 `app_deepseek.py`（DeepSeek 版，只改 `base_url` 与 `model`）
- **工作流逻辑**：理解这个教程的关键是 **Streamlit 的 rerun 模型**——脚本不是「跑一次」，而是**每次用户交互都从上到下重新执行整个脚本**
  - **单轮链路**：`load_dotenv` + 建 client → 定义三个函数 → `st.set_page_config` + 标题 → `st.sidebar.file_uploader`（有上传则 `process_uploaded_file` 解析出 `file_content`）→ 初始化/渲染 `st.session_state.messages` → `st.chat_input` 拿到 `user_msg` → append 用户消息 → `generate_response(user_msg, file_content)` → append assistant 消息 → 脚本结束、页面渲染完毕
  - **数据流**：`st.session_state.messages`（`list[{"role", "content"}]`）是**跨 rerun 的唯一持久状态**——每次重跑都先 `if "messages" not in st.session_state` 初始化、空时塞入 greeting、再 `for msg in ...` 全量重渲染。注意 `file_content` 是**普通局部变量**、不存 session_state，每次 rerun 都从 file_uploader 控件重新解析
  - **控制流**：`process_uploaded_file` 三分支（`application/pdf` / `text/plain` / 其它返回不支持）；`generate_response` 里 `if file_content` 决定是否注入 system 上下文；另有 `if uploaded_file is not None`、`if "messages" not in ...`、`if not st.session_state.messages`、`if user_msg := st.chat_input(...)`（海象运算符）
  - **循环与交互**：**没有 while**——交互由 Streamlit 的 rerun 循环驱动（用户提交 → 脚本重跑 → 渲染新状态）
  - **一个值得注意的实现细节**：`generate_response` 每次只构造「(可选)一条含 `file_content` 的 system 消息 + 当前一条 user 消息」，**不把 `session_state.messages` 的历史发给 LLM**——模型调用是无状态的，历史仅用于 UI 展示（所以它没有真正的对话记忆）
- **关键文件**：`building-chatbot-notebook.ipynb`（主教程）；`app.py`（OpenAI 版应用）；`app_deepseek.py`（DeepSeek 版）；`requirements.txt`
- **外部依赖**：OpenAI API key（或兼容 OpenAI 接口的其他模型 key）；streamlit、openai、python-dotenv、PyPDF2

#### 23. [fine-tuning-agents](tutorials/fine-tuning-agents/) — 微调让模型懂领域
- **解决什么问题**：通用模型不懂银行客服这类领域规则与安全边界，通用 prompt 无法覆盖。用监督微调（SFT）把领域能力打进模型。
- **实现了什么**：
  - 构造银行领域的 **JSONL 训练数据**（每行一个 `messages` 对象，含 `system` / `user` / `assistant`），并讲数据质量最佳实践
  - 按 80/20 划分 train / validation，用 `validate_jsonl` 校验格式
  - 用 OpenAI Python client 上传文件（`purpose="fine-tune"`）并创建微调任务（base model `gpt-4o-mini-2024-07-18`，suffix `banking-support`）
  - 轮询监控任务状态，拿到 `fine_tuned_model` 标识（如 `ft:gpt-4o-mini:...`）
  - 用 LangGraph 的 `create_react_agent` 集成微调模型并绑定工具（`account_lookup`、`transfer_payment`），**对比 base LLM 与微调模型**在领域专长与安全上的差异
- **工作流逻辑**：完整的「上传 → 创建 → 轮询 → 使用」链路
  - **① 造数据**：`kb_docs`（银行领域知识库 dict）→ `generate_diverse_examples(kb_doc)` 用**三重嵌套 for** 做笛卡尔积（每个 subtopic × 3 条 system_msg × 6 条 question × 4 条 response）→ `random.shuffle`
  - **② 切分落盘**：shuffle 后按 80/20 切 `train_examples` / `validation_examples` → 逐行写 `bank_finetune_data/train.jsonl` 与 `validation.jsonl`
  - **③ 校验**：`validate_jsonl` 逐行 `json.loads` 检查 `messages` 字段及每条 `role` / `content`
  - **④ 上传**：`client.files.create(file=..., purpose="fine-tune")` → 拿 `train_file_id` / `validation_file_id`
  - **⑤ 创建任务**：`client.fine_tuning.jobs.create(training_file, validation_file, model="gpt-4o-mini-2024-07-18", suffix="banking-support")` → 拿 `job.id`
  - **⑥ 轮询**：`while True` 每 30 秒 `retrieve(job.id).status`，`succeeded` / `failed` / `cancelled` 时 `break` → 取 `fine_tuned_model`（形如 `ft:gpt-4o-mini:banking-support:...`）
  - **⑦ 使用**：`ChatOpenAI(model=fine_tuned_model, temperature=0.0)` + `create_react_agent(tools=[account_lookup, transfer_payment])` → 对 `test_queries` 逐个 `invoke`
  - **数据流**：`kb_docs` → `examples`（list[dict]）→ shuffle/split → 磁盘 JSONL → file id → `job.id` → 轮询得到 `fine_tuned_model` 字符串 → 作为 `ChatOpenAI(model=...)` 注入 agent → `{"messages": [...]}` 进、`response["messages"]` 出
  - **控制流**：三重嵌套 for（笛卡尔积）；`validate_jsonl` 逐行 for + `try/except` 提前 return；轮询 `while True` + 终端状态 `break`；使用阶段 `for query` + 内层 `for msg in reversed(response["messages"])`，命中 `AIMessage` 且内容非空时 `break`
  - **循环与交互**：`while True` 轮询（30 秒间隔）是核心循环；另有多个嵌套 for。无用户输入循环
- **关键文件**：`fine_tuning_agents_guide.ipynb`（主教程）；运行时生成 `bank_finetune_data/`（train.jsonl、validation.jsonl）
- **外部依赖**：OpenAI API key（微调需计费）；openai、langchain、langgraph、tiktoken、pandas、scikit-learn

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

## 七、本地新增内容（非原始仓库）

以下内容是在原仓库基础上本地新增的，**不属于 Nir Diamant 的原始项目**。目前已提交在分支 **`study`** 上：

| 内容 | 说明 | 是否进 git |
|---|---|---|
| 29 个 `*-zh.ipynb` | 各教程的中文翻译版（只翻译文字，代码原样） | 已提交 |
| 16 个 `README.zh.md` | 各教程 README 的中文翻译版 | 已提交 |
| [README.zh.md](README.zh.md) · [STRUCTURE.md](STRUCTURE.md) | 中文根 README、本文档 | 已提交 |
| 45 个英文原文件 | 补上指向中文版的**正向链接** | 已提交 |
| `tutorials/agent-with-streamlit-ui/app_deepseek.py` | DeepSeek/内网网关适配版（原 `app.py` 是 OpenAI 版） | 已提交 |
| [tutorials/fixed-vs-autonomous-expense/](tutorials/fixed-vs-autonomous-expense/) | 可跑的对比实验：同一套报销审核业务，A 版全固定 vs B 版「固定骨架 + 自主格子」 | 已提交 |
| [tutorials/LangGraph-agent/](tutorials/LangGraph-agent/) 下的 `README.md` + `01-mental-model.md` ~ `05-pitfalls.md` | LangGraph 心智模型与拆解方法（6 篇指南） | 已提交 |
| `tutorials/agent-with-streamlit-ui/.env` | 存 `DEEPSEEK_API_KEY` | ⚠️ **被忽略，未提交** |
| `tutorials/agent-with-streamlit-ui/venv/` | Python 虚拟环境 | 被忽略 |

> 注意：`app_deepseek.py` 里硬编码了内网网关地址 `https://ai-api.d-robotics.cc/v1`。若要把该分支推送到公开仓库，建议先把 `base_url` 改为从环境变量读取。

---

## 八、快速上手 / 推荐阅读顺序

1. 读 [README.md](README.md) 的「Introduction」和「Tutorials」两节 → 拿到主题地图
2. 读 [CONTRIBUTING.md](CONTRIBUTING.md) → 理解单个教程的标准结构
3. 挑一个代表性教程深入：
   - 学核心框架 → [LangGraph-agent](tutorials/LangGraph-agent/)（先读目录里的 [README.md](tutorials/LangGraph-agent/README.md) 指南，再跑 notebook）
   - 学 API 化 → [fastapi-agent](tutorials/fastapi-agent/)（唯一带 tests 的工程化教程）
4. 之后按兴趣主题扫其余教程，先看各自的 README 建立概念即可
