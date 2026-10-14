# 01 · 心智模型：图、State、节点

## 一句话

LangGraph 是一个 **可编排的流程图引擎**。

你用代码声明「有哪些步骤、什么顺序、什么条件下分叉」，它负责按这个声明去执行、在步骤之间搬运数据。

---

## 三个必须先纠正的误解

### ❌「它是一个业务流逻辑设计的模板」

它是 **引擎**，不是模板。

区别在于：**模板是复制粘贴来改的，引擎是 import 来调用的。**

```python
from langgraph.graph import StateGraph, END   # ← import，不是复制
```

可复用的不是某段代码，是 **「图 + State + 节点」这个模式**。你的业务和仓库里那个「分类 → 抽实体 → 摘要」的教程长得完全不一样，但用的是同一个引擎。

### ❌「它是用来处理用户提问的」

不一定。本目录那个入门教程 [`langgraph_tutorial-zh.ipynb`](langgraph_tutorial-zh.ipynb) 的输入是一篇 **文章 / 文档**（变量名叫 `sample_text`），不是用户提问。它的流程是：

```
classification_node → entity_extraction → summarization → END
```

输什么由你定。可以是提问、文档、一张报销单、一个 HTTP 请求体。

### ❌「节点就是函数，所以节点之间可以互相调用」

**不可以。这是最反直觉、也最重要的一条。**

节点之间 **从不互相调用**。它们都只跟一个共享的 State 对象打交道：

```
    validate_receipt                classify_expense
           │                                │
           │ 读 receipt_text                │ 读 receipt_text
           │ 写 is_valid                    │ 写 expense_type, amount
           ▼                                ▼
    ┌────────────────────────────────────────────────┐
    │                    State                       │
    └────────────────────────────────────────────────┘
```

`validate_receipt` 根本不知道 `classify_expense` 存在。它只是往 State 里写了 `is_valid`，至于谁读、什么时候读，它不关心。

**这个设计的好处**：你可以随便插节点、删节点、换顺序，只要保证「我读的字段有人写、我写的字段有人认」就行。

—— 这就是为什么在配套项目里，我能把第 3 个节点的整个实现换掉（一次 LLM 调用 → 一个自主 Agent），而外面那张图一行都不用改。

---

## 三件东西

### 图（Graph）—— 骨架

回答「**谁先谁后、什么时候分叉**」。由这几样东西声明：

| 声明 | 作用 |
|---|---|
| `add_node(name, fn)` | 有哪些步骤 |
| `set_entry_point(name)` | 从哪开始 |
| `add_edge(a, b)` | 无条件的下一步 |
| `add_conditional_edges(a, fn, {...})` | 有条件的分叉 |
| `END` | 结束 |

### State —— 唯一的数据容器

一个 `TypedDict`。**整张图里只有这一个数据对象**，所有节点读它、写它。

```python
class ExpenseState(TypedDict, total=False):
    receipt_text: str          # 输入
    employee: str              # 输入
    is_valid: bool             # ① 校验节点写
    invalid_reason: str        # ① 校验节点写
    expense_type: str          # ② 分类节点写
    amount: float              # ② 分类节点写
    check_result: Dict         # ③ 核对节点写
    opinion: str               # ④ 意见节点写
    approver: str              # ⑤⑥ 审批人节点写
```

`total=False` 表示「字段可以缺」。执行到一半时，后面的字段本来就还没有值 —— 这很正常，不是 bug。

> 注意那些注释。它们不是文档，是 **契约**：每个字段只有一个「主人」。加字段时一定要问「谁写它」—— 否则两个节点写同一个字段会互相覆盖（见 [05 · 常见错误](05-pitfalls.md)）。

### 节点（Node）—— 处理单元

就是一个 **普通 Python 函数**，签名固定：

```python
def validate_receipt(state: ExpenseState) -> Dict[str, Any]:
    r = llm_json(f"...{state['receipt_text']}...")
    return {"is_valid": ..., "invalid_reason": ...}
    #      ↑ 只返回【自己负责的字段】，不是完整 State
```

两个要点：

1. **入参是完整 State** —— 想看什么自己取
2. **返回的是「部分更新」** —— 引擎会把它合并回 State，你没返回的字段原样不动

第 2 点很多人一开始会搞错：不需要 `return {**state, "is_valid": ...}`，**只返回你改的那几个键就行**。

---

## 数据流 vs 控制流

这两个词最容易混。一句话分开：

> **控制流 = 箭头往哪走。数据流 = 数据从哪来、到哪去。**

### 控制流：节点之间的箭头

```
                                          ┌─→ notify_director ─→ END
validate ─→ classify ─→ check ─→ draft ───┤
                                          └─→ notify_manager  ─→ END
              │                     │
              └─ 无效 → END          └─ 按金额分叉
```

这是你在 `add_edge` / `add_conditional_edges` 里写的东西。**它决定执行顺序。**

### 数据流：每个节点读什么、写什么

控制流只管「谁先谁后」，它 **不管数据怎么传**。数据是靠 State 传的：

| 节点 | 读 State | 写 State |
|---|---|---|
| `validate_receipt` | `receipt_text` | `is_valid`, `invalid_reason` |
| `classify_expense` | `receipt_text` | `expense_type`, `amount` |
| `check_expense` | `receipt_text`, `expense_type`, `amount`, `employee` | `check_result` |
| `draft_opinion` | `expense_type`, `amount`, `check_result` | `opinion` |
| `notify_director` / `notify_manager` | `amount` | `approver` |

**这张表就是数据流。** 注意它是「横向」的 —— 每个节点都独立地连着 State，不是 `validate` 把数据「传给」`classify`。

### 为什么这个区分有用

因为它解释了两种完全不同的 bug：

| 症状 | 病因 | 去哪看 |
|---|---|---|
| 执行顺序不对、该走的路径没走 | **控制流**问题 | 边和路由函数 |
| 节点拿到的值是空的 / 是旧的 | **数据流**问题 | State 字段的读写表 |

调试时先分清是哪一类，能省一半时间。

### 顺带：「循环」在哪

控制流里可以有环 —— 一个节点指回上游，就形成循环（重试、多轮工具调用都靠这个）。本目录的入门教程 [`langgraph_tutorial-zh.ipynb`](langgraph_tutorial-zh.ipynb) 里没有环，每次 `invoke()` 都是一次性的单遍执行。

但 **自主格子内部是有的** —— [02 · 自主度阶梯](02-autonomy-ladder.md) 会讲。

---

## 一个最小可跑的图

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class State(TypedDict, total=False):
    text: str
    upper: str

def to_upper(state: State) -> dict:
    return {"upper": state["text"].upper()}      # 只返回自己负责的字段

def add_suffix(state: State) -> dict:
    return {"upper": state["upper"] + "!!!"}

w = StateGraph(State)
w.add_node("to_upper", to_upper)
w.add_node("add_suffix", add_suffix)
w.set_entry_point("to_upper")
w.add_edge("to_upper", "add_suffix")
w.add_edge("add_suffix", END)

app = w.compile()
print(app.invoke({"text": "hello"}))
# {'text': 'hello', 'upper': 'HELLO!!!'}
```

**注意 `invoke` 返回的是完整 State。** 外部要取值就 `result["upper"]`。

---

## 什么时候加条件边

入门教程里有一个「增强版」，加了 `sentiment_analysis` 节点 —— 那只是纯线性多加一步，`add_edge` 串起来就行。

它还有一个「条件版」，在分类后分叉：

```python
def route_after_classification(state: EnhancedState) -> str:
    category = state["classification"].lower()
    return category in ["news", "research"]     # → True / False

conditional_workflow.add_conditional_edges("classification_node",
    route_after_classification, path_map={
        True:  "entity_extraction",   # 新闻 / 研究 → 抽实体
        False: "summarization",       # 其他       → 直接摘要
    })
```

**要点**：路由函数 **不干活，只回答「下一步去哪」**。判据全部来自 State —— 它不调用 LLM，也不做业务处理。

> ⚠️ 这个例子里的判据很「薄」：只是字符串比较（`category in [...]`）。真正的分叉判据可以是任何东西 —— 包括「LLM 说该走哪条」。这就是下一章要讲的自主度。

---

## 本章小结

- LangGraph 是 **引擎**不是模板，import 来用，不是复制来改
- 输入由你定，不一定是「用户提问」
- **节点之间从不互相调用**，全部通过 State 交换数据
- 节点返回 **部分更新**，引擎负责合并
- **控制流 = 箭头**，**数据流 = 每个节点读写哪些 State 字段**
- 路由函数只决定「下一步去哪」，不干活
