> 📄 English: [README.md](README.md)

![](https://europe-west1-atp-views-tracker.cloudfunctions.net/working-analytics?notebook=tutorials--agent-security-apex--readme)

# Agent 安全评估教程

## 概述

通过对 AI 系统进行动手安全测试，学习提示注入（prompt injection）攻击与防御。你不仅仅是阅读漏洞相关知识，而是会实际利用这些漏洞，然后使用真实的攻击数据集和自动化测试工具来构建针对它们的防护。

## 你将学到什么

- **攻击技术**：掌握 8 大类提示注入攻击，包含 91 个真实示例
- **自动化测试**：使用专业的安全测试工具评估 AI 系统漏洞
- **防御实现**：使用高级提示工程（prompt engineering）构建并验证安全措施
- **编码绕过**：测试攻击者用来绕过过滤器的 12 种不同混淆方法

## 教程

### **[完整安全评估：agent-security-evaluation-tutorial.ipynb](./agent-security-evaluation-tutorial.ipynb)**
动手教程，涵盖攻击技术、自动化测试和防御实现，并配有真实示例。

## 快速开始

1. **安装包**：`pip install openai python-dotenv pandas`
2. **设置 API key**：创建包含 `OPENAI_API_KEY=your_key_here` 的 `.env` 文件
3. **运行教程**：通过自动化和手动测试，在 30-45 分钟内完成

## 包含的文件

- **主教程** —— 完整的安全评估 notebook
- **测试框架** —— 自动化安全测试工具
- **攻击工具** —— 编码和混淆工具
- **防御示例** —— 生产就绪的安全提示
- **攻击数据集** —— 91 个已记录的真实攻击示例

## 警告

本教程出于教育目的演示了真实的攻击技术。请仅在你自己拥有或已获得明确测试授权的系统上使用。
