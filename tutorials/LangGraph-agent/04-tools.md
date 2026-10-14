# 04 · 工具从哪来

## 一句话

工具 = **给 LLM 看的说明书（docstring）+ 本地真实执行的代码**。

外面那层说明书发给 LLM，里面那段代码在本机跑。**LLM 只看得到说明书。**

---

## 工具长什么样

```python
@tool
def query_approval(po_number: str) -> str:
    """查询采购审批单的批复额度、申请人和状态。输入采购单号，例如 PO-2024-0156。"""
    r = APPROVALS.get(po_number.strip().upper())
    if not r:
        return f"审批系统中未找到采购单号 {po_number}。"
    return f"采购单 {po_number}：批复额度 {r['approved_amount']} 元，..."
```

`@tool` 这个装饰器干的事：把 **函数签名 + docstring** 转成一份 JSON Schema 发给 LLM。

### 由此推出两条硬约束

**① docstring 不是注释，是 API 契约。**

它直接决定 LLM 会不会用这个工具、参数传得对不对。写得含糊 → 模型乱调或不调。

要写清三件事：**干什么、参数是什么、长什么样（给例子）**。

**② 返回值必须是字符串。**

LLM 要读它。查完数据库要 `json.dumps(...)` 或拼成自然语言。

```python
return f"采购单 {po_number}：批复额度 {r['approved_amount']} 元，..."   # ✅
return {"approved_amount": 5000}                                      # ❌ LLM 读不了
```

配套项目里每个工具都返回一句中文，就是为此。

### 错误也要返回成文本，不要抛异常

```python
if not r:
    return f"审批系统中未找到采购单号 {po_number}。"
```

**读者是 LLM。** 一句能看懂的话比堆栈有用得多 —— 它看到「没找到」会去试别的，看到异常可能直接崩。

---

## 工具从哪来：四条路

### ① 自己写 —— 内部系统，没得选

只要数据在 **你自己公司的系统** 里（ERP、审批、内部数据库），市面上没有现成工具。只能自己包一层：

```python
@tool
def query_approval(po_number: str) -> str:
    """查询采购审批单的批复额度、申请人和状态。"""
    r = requests.get(f"https://erp.internal/api/po/{po_number}", timeout=5).json()
    return f"采购单 {po_number}：批复额度 {r['approved_amount']} 元，..."
```

**只改函数体，图的代码一行不动** —— 这就是把工具独立在 `expense_common.py` 里的意义。

> ⚠️ 这一段是 agent 落地 **最脏最累** 的部分，通常占整个项目 **80% 的工作量**。
> 不是写图难，是接系统难：认证、限流、超时、字段格式、异常兜底、权限隔离。

### ② 接现成的 —— 框架预置工具包

有些能力别人早写好了：

| 工具 | 干什么 |
|---|---|
| `TavilySearchResults` | 联网搜索（[`agent-with-tavily-web-access`](../agent-with-tavily-web-access/)） |
| `SQLDatabaseToolkit` | **接上数据库，自动生成一整套查库工具**（连 `query_xxx` 都不用自己写） |
| Wikipedia / Arxiv / GitHub / Slack / Gmail | 各类封装 |

用法就是塞进列表，和自写的混着放：

```python
TOOLS = [TavilySearchResults(), query_approval, query_order]
```

**对 LLM 来说它们长得一样。**

### ③ 接 MCP —— 现在最主流

MCP（Model Context Protocol）把「工具」变成 **跨语言、跨进程的标准接口**。别人写好的 MCP Server 直接挂，**完全不用碰它的实现代码**。

仓库里的例子：[`agent-with-mcp`](../agent-with-mcp/)。服务端 [scripts/mcp_server.py](../agent-with-mcp/scripts/mcp_server.py)：

```python
mcp = MCPServer("crypto-price-tracker")

@mcp.tool()
async def get_crypto_price(crypto_id: str, currency: str = "usd") -> str:
    """Get the current price of a cryptocurrency in a specified currency."""
    ...
mcp.run(transport="stdio")
```

客户端用 `stdio_client` + `ClientSession` 连上去，取工具绑给 agent。

**关键优势**：这个 server 可以是 Node.js / Go 写的、跑在另一台机器上 —— 你只管连。

GitHub 官方 MCP Server、Postgres、Filesystem、Slack 都是现成的。你在 Claude Desktop、Cursor 里配的那些 MCP，就是同一个东西。

### ④ 把别的 Agent 当工具

[`a2a`](../a2a/)（Agent2Agent 协议）—— 你的 agent 调用另一个独立 agent。

本质也是工具，只是对方更聪明。

---

## 什么时候需要工具

| 情况 | 要不要工具 |
|---|---|
| 模型本来就会（写作、翻译、算术、常识） | ❌ 不用，直接问 |
| 数据是 **私有的**（内部系统、数据库） | ✅ 必须 |
| 数据要 **实时**（股价、库存、天气） | ✅ 必须 |
| 模型知道但 **容易记错**（具体金额、日期、条款号） | ✅ 写，让它去查而不是靠记忆 |

最后一条最重要：

> **模型能编出一个「看起来合理」的答案，但它编不出「这张单子的批复额度是 5000」—— 这个事实只有查才拿得到。**

配套项目 A 版那句「3600 = 2400 + 1200，算得对，未发现异常」，就是模型在 **用流畅的语言填它没有的信息**。

这不是模型笨，是你没给它查的工具。

---

## 工具是「能力边界」，不是「能力扩展」

这句要说三遍：

> **自主 Agent 的能力上限，是你给它的工具集定的，不是它自己长的。**

配套项目 README 的练习 1 就是验证这个：**把 B 版的工具从 5 个砍到 1 个（只留 `query_approval`）**，单据 1 的行程天数问题它就 **永远查不出来** 了 —— 不是它不聪明，是它手上没那个工具。

反过来说，**工具给多了也是坏事**：

| 问题 | 后果 |
|---|---|
| 工具太多 | 模型更容易挑错、幻觉出根本不存在的工具名 |
| 工具职责重叠 | 模型在几个相似工具间反复横跳，白烧调用 |
| 工具描述含糊 | 调了但参数传错 |

**原则：只给这一格真正需要的工具。**

---

## 一个实操提醒：工具返回的数据从哪来

配套项目用的是 5 个硬编码 dict（[`expense_common.py:87-114`](../fixed-vs-autonomous-expense/expense_common.py#L87-L114)），**纯假数据、无 IO**。

为什么故意用假数据：

1. **陷阱必须是「文本里看不出、后端里查得到」** —— 才能精确控制对比
2. **零外部依赖，可复现** —— clone 下来配个 key 就能跑
3. **跑得快** —— 没有网络延迟

这也决定了结论的边界：**demo 里「查得到」是免费的，真实系统里查一次就是一次网络请求。**

---

## 本章小结

- 工具 = **docstring（给 LLM 的契约）+ 本地执行的代码**
- **docstring 要认真写** —— 它是 API 契约，不是注释
- **返回值必须是字符串**；错误也返回文本，别抛异常
- 四条路：**自写 / 预置工具包 / MCP / A2A**
- 工具是 **能力边界**：砍掉工具 = 砍掉能力；给多了 = 增加幻觉面
- 判据：**私有数据、实时数据、模型容易记错的事实 → 需要工具**
