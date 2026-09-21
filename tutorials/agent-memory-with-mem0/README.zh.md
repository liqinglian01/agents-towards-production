> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-memory-with-mem0--readme)

# 使用 Mem0 为 AI Agent 构建持久化记忆

使用 Mem0 的混合存储架构构建具有持久、不断演化的记忆的智能 AI agent。学习实现能够持续从用户交互中学习并随时间自我改进的自适应记忆系统。

## **🎯 你将学到什么**

- **存储长期知识**，使用向量数据库进行语义召回
- **将概念映射到知识图谱**，利用 Mem0 的图记忆能力
- **融合结构化和非结构化记忆**，回答更丰富的研究查询
- **教会 agent 用户特定的偏好**，并在后续会话中使用该上下文
- **检索正确的信息**，结合嵌入和图遍历

## **📓 教程**

[Mem0 Tutorial Notebook](mem0_tutorial.ipynb)

## **🚀 在 Google Colab 中运行**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NirDiamant/agents-towards-production/blob/main/tutorials/agent-memory-with-mem0/mem0_tutorial.ipynb)

## **需求**

- **[Mem0](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-memory-with-mem0--readme&click=mem0-nir&target=https%3A%2F%2Fmem0.dev%2Fgithub%2Fnir&text=Mem0)**（开源）
- **OpenAI API Key**：用于 LLM 推理和嵌入
- **Qdrant 或 Mem0 支持的其他向量存储**：用于语义搜索的向量数据库
- **Neo4j 或 Mem0 支持的其他图数据库**：用于关系映射的图数据库

## **🎓 你将构建什么**

**个人 AI 研究助手**，它能：

- 维护智能记忆，自动提取并存储研究兴趣
- 使用图存储映射论文、作者和概念之间的知识关系
- 通过自我改进的记忆能力适应用户偏好
- 使用混合记忆检索提供上下文相关的帮助
- 从每次研究对话中学习并演化
