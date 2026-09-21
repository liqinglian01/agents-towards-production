> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-file-conversion-with-hushvert--readme)

# 为你的 Agent 赋予文件转换能力（本地、私有）

Agent 收到的是文件，而不是提示词：季度汇报、合同、电子表格、扫描件。模型无法原生读取其中任何一种，而常见的补救办法（把所有文件都上传到转换 API）是一种隐私倒退，也是为用户设备本来可以免费完成的工作支付的一笔计费账单。本教程构建了生产级答案：一个双车道转换方案，在设备能够处理时始终本地转换，只为真正需要服务器的 Office 文档格式计费。

## 概述

本教程中的一切都围绕一条路由规则展开：绝不为设备自己能完成的转换付费——无论是金钱还是隐私。

- **本地车道**是 [`@hushvert/engine`](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-file-conversion-with-hushvert--readme&click=hushvert-engine-npm&target=https%3A%2F%2Fwww.npmjs.com%2Fpackage%2F%40hushvert%2Fengine&text=%40hushvert%2Fengine)，一个 MIT 许可的 WebAssembly 引擎：图片、HEIC、音频、压缩包、PDF 页面操作和数据文件完全在浏览器中转换。字节绝不触及网络，你可以在自己的网络标签页中验证这一点。
- **服务器车道**覆盖浏览器无法完成的事情（Office 文档转 PDF、PDF 转 Word、PDF/PPTX/XLSX 转 LLM 就绪的 markdown、大视频），以两种方式暴露：你的 Agent 作为工具调用的 MCP 服务器，以及供流水线使用的普通 REST API。

## 你将学到什么

- **双车道路由规则** - 哪些转换绝不需要离开设备，以及如何强制执行这种划分，让 Agent 永远不在客户端可转换的格式上消耗积分。
- **转换作为工具调用** - 一个配置块即可让 Claude Code、Cursor 或任何 MCP host 拥有处理重量级格式的 `convert_file` 工具。
- **托管 API 流程** - 从 Python 提交、上传、轮询、下载，带幂等 key 和诚实的失败状态。
- **以怀疑态度解读保真度声明** - 一个基准测试，展示转换后的 markdown 在哪些方面胜过流行的提取器（多栏阅读顺序），以及哪些方面没有（简单表格已是一个被解决的问题）。

## 教程

### [完整教程：agent-file-conversion-tutorial.ipynb](./agent-file-conversion-tutorial.ipynb)

## 在 Google Colab 中运行

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NirDiamant/agents-towards-production/blob/main/tutorials/agent-file-conversion-with-hushvert/agent-file-conversion-tutorial.ipynb)

## 要求

- notebook 需要 Python 3.10+
- 服务器车道部分需要一个 hushvert API key：在 [hushvert.com/developers/keys](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-file-conversion-with-hushvert--readme&click=hushvert-keys&target=https%3A%2F%2Fhushvert.com%2Fdevelopers%2Fkeys%3Futm_source%3Dagents-towards-production%26utm_medium%3Dgithub%26utm_campaign%3Dtutorial&text=hushvert%20developer%20keys) 创建免费账号和 key（一次性邮箱验证码，无需密码；key 需要已确认的邮箱）。每月免费额度足以覆盖整个教程，无需付费。
- 仅当你把 MCP 服务器连接到本地 Agent 时，才需要 Node.js 18+

## 你将构建什么

一个面向生产 Agent 的文档接入方案：零成本、零泄露的本地车道转换，一个针对重量级格式的计费服务器车道，以及一条基于基准测试的规则，用于在重构与原始文本提取之间做出选择。
