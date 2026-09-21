> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-with-tavily-web-access--readme)

# 使用 Tavily 为你的 Agent 赋予 Web 访问能力


## 概述

本教程系列面向希望为其 AI Agent 赋予实时 Web 访问能力的 Python 开发者，让 Agent 能够利用最新信息作为上下文。对于需要执行研究、准确回答问题、监控趋势或提供最新建议的 AI Agent 而言，实时 Web 信息至关重要。你将学习如何构建能够搜索网络、提取有价值内容、智能浏览网站，并将实时 Web 信息集成到私有知识库中的 AI Agent。

## 议程

本教程系列遵循循序渐进的学习路径，包含三个独立的教程：
1. 在[教程 #1](./search-extract-crawl.ipynb)中，我们将介绍 **Web 访问的基础知识**。

2. 在[教程 #2](./web-agent-tutorial.ipynb)中，我们将**构建一个能够搜索、抓取和爬取网络的 Web Agent**。

3. 最后，在[教程 #3](./hybrid-agent-tutorial.ipynb)中，我们将开发一个系统，**将实时 Web 信息与私有知识库数据相结合**。


## 目录结构

```
📁 agent-with-tavily-web-access/
├── 📓 search-extract-crawl.ipynb  # Tutorial notebook 1
├── 📓 web-agent-tutorial.ipynb    # Tutorial notebook 2
├── 📓 hybrid-agent-tutorial.ipynb # Tutorial notebook 3
├── 📁 assets/                     # Diagrams and screenshots
│   ├── 🖼️ web-agent.svg
|   ├── 🖼️ hybrid.svg
|   ├── 🖼️ api-key.png
│   └── 🖼️ sign-up.png
├── 📁 supplemental/                # Supplemental materials
│   ├── 📓 vectorize_tutorial.ipynb # Vectorize your own documents
│   ├── 📁 docs/                    # Sample CRM documents
│   └── 📁 db/                      # Pre-built Chroma vector database
└── 📄 README.md                    # This file
```
