# LangGraph 心智模型与拆解方法

> 📄 English: *(this guide is Chinese-only)*

这不是 API 手册。API 手册告诉你「有哪些函数」，这份材料回答的是另一个问题：

> **拿到一个业务需求，我该怎么把它变成一张能跑的图？**

配套代码：[`tutorials/fixed-vs-autonomous-expense/`](../fixed-vs-autonomous-expense/) —— 一个可跑的「固定骨架 vs 固定骨架 + 自主格子」对比项目。本材料里的每个结论，都能在那个项目里找到对应的代码行。

---

## 本目录内容

| 文件 | 是什么 |
|---|---|
| [`langgraph_tutorial.ipynb`](langgraph_tutorial.ipynb) · [`-zh`](langgraph_tutorial-zh.ipynb) | 仓库自带的 LangGraph 入门教程 notebook（分类 → 抽实体 → 摘要） |
| [`01-mental-model.md`](01-mental-model.md) ~ [`05-pitfalls.md`](05-pitfalls.md) | 本指南：心智模型 + 拆解方法（见下方学习路径） |

> **notebook 是「跑一遍」，本指南是「讲清楚为什么」。** 建议先跑 notebook 有个感性认识，再回来读指南。

---

## 这份材料解决哪些困惑

| 困惑 | 去哪一章 |
|---|---|
| 图、State、节点到底指什么？怎么设计？ | [01 · 心智模型](01-mental-model.md) |
| 「数据流」和「控制流」是什么意思？ | [01 · 心智模型](01-mental-model.md#数据流-vs-控制流) |
| 它是不是一个「业务流逻辑模板」，方便加节点？ | [01 · 心智模型](01-mental-model.md#三个必须先纠正的误解) |
| 它是用来处理「用户提问」的吗？ | [01 · 心智模型](01-mental-model.md#三个必须先纠正的误解) |
| 固定流程图和 Agent 自主判断怎么协同？ | [02 · 自主度阶梯](02-autonomy-ladder.md) |
| 每个节点的 LLM 判断依据从哪来？ | [02 · 自主度阶梯](02-autonomy-ladder.md#判断依据的权威性阶梯) |
| 实际做的时候步骤是什么？ | [03 · 拆解思路](03-design-method.md) |
| 节点该怎么切？切多细？ | [03 · 拆解思路](03-design-method.md#step-3--节点划分判据) |
| 工具必须自己写吗？能接现成的吗？ | [04 · 工具从哪来](04-tools.md) |
| 我这么写对不对？ | [05 · 常见错误](05-pitfalls.md) |

---

## 学习路径

四步，一步比一步具体：

1. **建立心智模型** —— [01](01-mental-model.md)
   搞清图 / State / 节点，以及最容易搞混的「数据流 vs 控制流」
2. **理解自主度** —— [02](02-autonomy-ladder.md)
   固定和自主不是二选一，是同一个图上的不同格子
3. **掌握拆解方法** —— [03](03-design-method.md)
   从需求到可运行的图，5 步 + 迭代
4. **备好工具箱** —— [04](04-tools.md)
   工具从哪来、什么时候用、docstring 怎么写

[05](05-pitfalls.md) 是常见错误 + 速查表，写代码和调试时对照着看。

---

## 前置知识

- 会写 Python
- 用过 LLM API（调过 `chat.completions` 或 `ChatOpenAI` 之类）
- **不需要**做过 Agent

---

## 配套材料

| 材料 | 用途 |
|---|---|
| [`fixed-vs-autonomous-expense/`](../fixed-vs-autonomous-expense/) | 本材料的配套可跑项目 |
| [`agent-with-mcp/`](../agent-with-mcp/) | 工具怎么通过 MCP 接入 |
| [`a2a/`](../a2a/) | 把别的 Agent 当工具 |

---

## 一句话浓缩

> 先问该不该上图 → 找决策点（一次带出图 / 节点 / State）→ 骨架先跑通
> → 逐格填实现并定自主度 → 给需要的那几格配工具 → 回头改图。
