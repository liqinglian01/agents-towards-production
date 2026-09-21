> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-security-with-llamafirewall--readme)

# 面向 AI Agent 安全的 LlamaFirewall 教程

## 概述

使用 **LlamaFirewall** —— 一个为生产级 AI 系统提供全面护栏的开源安全框架 —— 来保护你的 AI agent 免受安全威胁。学习如何实现输入验证、输出监控和工具安全，以构建安全、生产就绪的 agent。

<div align="center">
<img src="assets/tools-security.png" alt="LlamaFirewall Tools Security Interface" width="600"/>
</div>

## 你将学到什么

- **输入安全**：防范提示注入（prompt injection）和有害内容
- **输出验证**：确保 agent 响应符合预期行为
- **工具安全**：防止未经授权的工具使用和资源滥用
- **实时监控**：通过全面的日志记录跟踪安全事件
- **生产部署**：在实际应用中实现安全措施

## 教程

### **[Hello Llama: hello-llama.ipynb](./hello-llama.ipynb)**
基础消息扫描，用于检测和阻止潜在的有害内容。

### **[Input Guardrail: input-guardrail.ipynb](./input-guardrail.ipynb)**
验证用户输入，以防范恶意提示和注入攻击。

### **[Output Guardrail: output-guardrail.ipynb](./output-guardrail.ipynb)**
验证 AI agent 的响应，以确保其符合预期行为。

### **[Tools Security: tools-security.ipynb](./tools-security.ipynb)**
为 AI agent 工具提供全面的安全保护，包括输入验证和访问控制。

## 快速开始

1. **安装依赖**：`pip install -r requirements.txt`
2. **获取 API key**：OpenAI API key + 用于一致性检查的 Together AI key
3. **设置 HuggingFace**：申请访问 Llama Prompt Guard 2 模型
4. **配置**：运行 `llamafirewall configure` 来设置模型和 API key

## 作者
由 [Matan Kotick](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-security-with-llamafirewall--readme&click=linkedin-matan-kotick-664735252&target=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fmatan-kotick-664735252&text=Matan%20Kotick) 和 [Amit Ziv](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-security-with-llamafirewall--readme&click=linkedin-amit-ziv-49690b120&target=https%3A%2F%2Fwww.linkedin.com%2Fin%2Famit-ziv-49690b120&text=Amit%20Ziv) 创建。
