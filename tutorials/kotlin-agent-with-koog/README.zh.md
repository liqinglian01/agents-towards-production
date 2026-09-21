> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--kotlin-agent-with-koog--readme)

# 使用 Koog 在 Kotlin 中构建 AI Agent

用 JetBrains 的 Koog 框架在 [Kotlin](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--kotlin-agent-with-koog--readme&click=kotlinlang&target=https%3A%2F%2Fkotlinlang.org%2F%3Futm_source%3Dgithub%26utm_medium%3Dinfluencers%26utm_campaign%3Dkotlin_nir_supporter_1&text=Kotlin) 中构建你的第一个 AI Agent，从基础提示-响应式 Agent 逐步进阶到工具调用和结构化输出。

## 你将学到什么

- **Koog 基础**：用 Koog 搭建 Kotlin 项目，并创建一个向 LLM 发送提示词的最小 AI Agent
- **工具调用（Tool Calling）**：定义 Agent 可以自主调用的自定义工具，使用 ReAct 模式（Reason、Act、Observe）
- **结构化输出（Structured Output）**：从 LLM 获取带类型的 Kotlin 数据类，而不是自由格式的文本
- **Kotlin-Native AI**：利用 Kotlin 协程、序列化和类型安全进行 AI Agent 开发

## 快速开始

```bash
git clone https://github.com/NirDiamant/agents-towards-production.git
cd agents-towards-production/tutorials/kotlin-agent-with-koog

export OPENAI_API_KEY="sk-..."

./run.sh   # Interactive guided runner (recommended for first time)
```

或者直接运行每个步骤：

```bash
./gradlew step1   # Basic agent
./gradlew step2   # Agent with tools
./gradlew step3   # Structured output
```

已包含 Gradle wrapper——无需单独安装 Gradle。首次运行会自动下载依赖（大约需要一分钟）。

## 教程

[完整教程走读](tutorial.md)

## 环境要求

- **JDK 17+** 已安装（[Adoptium](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--kotlin-agent-with-koog--readme&click=adoptium&target=https%3A%2F%2Fadoptium.net%2F&text=Adoptium) 或 `brew install openjdk@17`）
- **OpenAI API Key**（已开启计费）

## 你将构建什么

一个智能助手，使用自定义工具（天气查询、计算、事实检索）回答问题，并以 Kotlin 数据类的形式返回带类型、结构化的响应。

**总教程时长**：约 25-30 分钟

**难度**：初级-中级（Kotlin 基础、Gradle）
