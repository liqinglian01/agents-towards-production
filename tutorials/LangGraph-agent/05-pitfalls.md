# 05 · 常见错误与速查表

写代码和调试时对照着看。

---

## 十七个坑

### 心智模型类

**1. 以为节点之间可以互相调用**

```python
def node_a(state):
    return node_b(state)      # ❌ 不要这样
```

节点只跟 State 打交道。要传数据就写进 State，让对方自己读。

**2. 以为要返回完整 State**

```python
return {**state, "is_valid": True}      # ❌ 多余
return {"is_valid": True}               # ✅ 引擎负责合并
```

**3. 以为 `invoke()` 返回的是某个节点的返回值**

它返回 **完整 State**。取值要 `result["字段名"]`。

**4. 把 LangGraph 当模板复制粘贴**

它是 **引擎**，`import` 来用的。可复用的是「图 + State + 节点」这个 **模式**，不是某段代码。

**5. 以为它只能处理「用户提问」**

输入由你定 —— 文档、报销单、HTTP 请求体都行。

---

### State 设计类

**6. 多个节点写同一个字段**

LangGraph 是合并语义，**后写的会覆盖先写的**。

铁律：**一个字段只有一个主人**。写 State 时给每个字段标注「谁写」。

**7. 把没人读的字段留在 State 里**

「有人写、没人读」→ 这不是 State，是那个节点的局部变量。删掉。

**8. 读取时不做兜底**

执行到一半时，后面的字段本来就还没值。

```python
state["amount"]                          # ❌ 可能 KeyError
float(state.get("amount", 0) or 0)       # ✅
```

---

### 节点划分类

**9. 节点切得太细**

一个节点干一件事（「抽金额」单独一个节点）→ 每多一个节点 = 多一次 LLM 调用 + 多一层状态传递。

**10. 节点切得太粗**

「审核报销单」一个大节点包办 → 那还不如直接用 L3 自主 Agent，**图白画了**。

> 自检：节点名连起来念一遍。
> 「校验 → 分类 → 核对 → 写意见」像 **业务阶段** ✅
> 「做 A → 做 B → 做 C」像流水账 ❌

---

### 自主度类

**11. 该用代码的地方用了 LLM**

```python
# ❌ 问 LLM「3600 大于 5000 吗」
# ✅
return "director" if amount > 5000 else "manager"
```

每找到这样一个地方，就省一次调用、去掉一个不确定源。

**12. 一上来就设计自主格子**

你会同时面对两类问题：流程错了吗？还是这一格自主得不对？

**先全固定跑通，再升级自主。**

**13. 没问「这一格的判断依据是第几级」**

最危险的是 **第 4 级（模型自己的世界常识）** —— 它 **错的时候说话最像对的**。

> A 版：「3600 = 2400 + 1200，算得对，未发现异常」
> 真实含义：「我没有信息去发现异常」

判据全部来自单据文本 + 模型常识 → **危险信号**。

---

### 工具类

**14. docstring 写得太随意**

它是 **给 LLM 看的 API 契约**，不是注释。要写清：干什么、参数是什么、长什么样（给例子）。

**15. 工具返回 dict**

LLM 读不了。必须返回字符串；错误也要返回成文本，**别抛异常**。

**16. 给不需要的节点配工具**

工具越多，模型越容易挑错、幻觉出不存在的工具。**只给这一格真正需要的。**

**17. 忘了「工具是能力边界」**

砍掉工具 = 砍掉能力。B 版砍到只剩 `query_approval`，行程天数的问题它 **永远查不出来**。

---

## 速查表

### 组装图

```python
from langgraph.graph import StateGraph, END

w = StateGraph(MyState)
w.add_node("name", fn)                        # 节点
w.set_entry_point("first")                    # 入口
w.add_edge("a", "b")                          # 无条件边
w.add_edge("last", END)                       # 结束
w.add_conditional_edges("a", route_fn, {      # 条件边
    "label1": "b",
    "label2": "c",
})
app = w.compile()
result = app.invoke({"field": value})
```

### 节点签名

```python
def my_node(state: MyState) -> dict:
    return {"field_i_own": value}     # 只返回自己负责的字段
```

### 路由函数

```python
def route_fn(state: MyState) -> str:
    return "label"        # 只决定去哪，不干活
```

### State

```python
class MyState(TypedDict, total=False):
    a: str      # ① 节点A 写
    b: int      # ② 节点B 写
```

### 自主格子（L2）

```python
# LangChain V1 把这个预置 Agent 从 langgraph.prebuilt 挪到了 langchain.agents
try:
    from langchain.agents import create_agent as create_react_agent
except ImportError:                                    # 老版本
    from langgraph.prebuilt import create_react_agent  # type: ignore

def check_autonomous(state) -> dict:
    agent = create_react_agent(model=get_llm(), tools=TOOLS)
    r = agent.invoke({"messages": [("human", f"...{state['x']}...")]})
    return {"result": r["messages"][-1].content}
```

### 统计 LLM / 工具调用次数

```python
from langchain_core.callbacks import BaseCallbackHandler

class Counter(BaseCallbackHandler):
    def __init__(self):
        self.llm_calls = 0
        self.tools = []

    def on_llm_start(self, *a, **k):        self.llm_calls += 1
    def on_tool_start(self, serialized, *a, **k):
        self.tools.append((serialized or {}).get("name", "?"))

app.invoke(inputs, config={"callbacks": [Counter()]})
```

---

## 设计检查清单

- [ ] **该不该上图**：三条都满足？（阶段 / 传数据 / 不是全自主）
- [ ] **决策点找齐** 了吗？每个带出哪些 State 字段？
- [ ] **State 每个字段有唯一写入者** 吗？有没有「没人读」的死字段？
- [ ] **每个节点边界** 上，判断 / 换自主度 / 传数据 至少发生一件吗？
- [ ] **节点名连起来念**，像业务阶段还是流水账？
- [ ] **每格的判断依据是第几级**？有没有该用 L0 却用了 LLM 的？
- [ ] **哪几格需要工具**？工具是自写还是能接现成的？
- [ ] **骨架跑通了** 吗？出 bug 时能定位到「流程」还是「某一格」吗？
- [ ] **加完工具后回看**，图要不要拆 / 并？

---

## 一句话总结

> 先问该不该上图 → 找决策点（一次带出图 / 节点 / State）→ 骨架先跑通
> → 逐格填实现并定自主度 → 给需要的那几格配工具 → 回头改图。

**这套方法不是 LangGraph 特有的** —— 换成别的编排框架也还是这一套。

LangGraph 只是「图 + State + 节点」这个模式的一个实现。真正可复用的是 **拆解思路**，不是那个 API。
