> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-memory-with-redis--readme)

# 🧠 使用 Redis 的 Agent 记忆

使用 Redis 和 LangGraph 构建一个**具备记忆能力的 AI agent**，它能记住用户偏好并从对话中学习。

## 🎯 你将学到什么

本教程的目标是让你掌握一个**横向通用概念**，可应用到自己的 agent 用例中。

- **双记忆架构**：实现短期（对话状态）和长期（持久化知识）记忆
- **语义搜索**：使用 RedisVL 配合嵌入进行语义记忆检索
- **记忆类型**：理解情景记忆（用户经历）与语义记忆（通用知识）模式的区别
- **生产模式**：基于工具的记忆管理和对话摘要
- **LangGraph 集成**：使用 Redis checkpointers 构建完整工作流，实现状态持久化

## 📓 教程

[Agent Memory Tutorial Notebook](agent_memory_tutorial.ipynb)

## 🚀 在 Google Colab 中运行

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NirDiamant/agents-towards-production/blob/main/tutorials/agent-memory-with-redis/agent_memory_tutorial.ipynb)

## 需求

- **OpenAI API Key**（需启用计费）
- **Redis**，可选在 Colab 中安装，或使用 [Redis Cloud](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-memory-with-redis--readme&click=redis-try-free&target=https%3A%2F%2Fredis.io%2Ftry-free%2F%3Futm_source%3Dnir%26utm_medium%3Dcpa%26utm_campaign%3D2025-05-ai_in_production-influencer-nir%26utm_content%3Dsd-software_download-7013z000001WaRY&text=Redis%20Cloud)

## 🎓 你将构建什么

一个旅行 agent，它能：
- 跨对话记住用户偏好
- 存储长期记忆（例如「我更喜欢 Delta 航空公司」）
- 基于过往交互提供个性化推荐
- 自动管理对话上下文

**总教程时长**：约 30-45 分钟
**难度**：中级（Python、LangGraph、工具调用，以及其他基础 AI 概念）
