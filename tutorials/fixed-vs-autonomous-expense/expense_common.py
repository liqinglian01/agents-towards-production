# -*- coding: utf-8 -*-
"""
报销单审核 ——「固定骨架 + 自主格子」对比实验 · 公共模块

★ 这个文件里装的是两版【完全相同】的部分：

    - LLM 配置（指向 OpenAI 兼容网关）
    - ExpenseState 定义
    - 5 个节点里的 4 个（校验 / 分类 / 生成意见 / 审批人）
    - 图本身的组装函数 build_graph()

★ 两版唯一的差异是第 5 个节点 check_expense 的函数体。

它通过 build_graph(check_fn) 的参数注入 —— 这正是本实验要演示的核心：
    「固定流程」和「自主判断」的差异，可以压缩到一个函数体里，
     而外面那张图的代码一行都不用改。
"""

import io
import json
import os
import re
import sys
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

load_dotenv()

# Windows 终端默认可能是 GBK，中文会乱码
for _s in ("stdout", "stderr"):
    _stream = getattr(sys, _s, None)
    if _stream is not None and getattr(_stream, "encoding", "").lower() not in ("utf-8", "utf8"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════
#  1. LLM 配置
# ══════════════════════════════════════════════════════════════════

MODEL = os.getenv("EXPENSE_MODEL", "deepseek-flash")
BASE_URL = os.getenv("EXPENSE_BASE_URL", "https://ai-api.d-robotics.cc/v1")


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(
        model=MODEL,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=BASE_URL,
        temperature=temperature,
    )


def _parse_json(raw: str) -> Dict[str, Any]:
    """网关不一定支持 structured output，所以用提示 + 容错解析。"""
    raw = (raw or "").strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.M).strip()
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return {"_raw": raw}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"_raw": raw}


def llm_json(prompt: str) -> Dict[str, Any]:
    raw = get_llm().invoke(
        prompt + "\n\n只输出 JSON，不要任何解释文字、不要 markdown 代码块。"
    ).content
    return _parse_json(raw)


# ══════════════════════════════════════════════════════════════════
#  2. 埋好的「假后端」—— 自主版要查的就是这里
#     ★ 关键设计：下面这些信息【单据文本里都没有】，
#       只有真的发起查询才能拿到。
# ══════════════════════════════════════════════════════════════════

APPROVALS = {
    # 采购审批单号 -> 批复额度
    "PO-2024-0156": {"approved_amount": 5000, "applicant": "张伟", "status": "已批准"},
    "PO-2024-0203": {"approved_amount": 12000, "applicant": "李娜", "status": "已批准"},
}

ORDERS = {
    # 订单号 -> 明细
    "SO-7781": {"item": "服务器硬盘", "qty": 20, "unit_price": 430, "total": 8600, "po": "PO-2024-0156"},
    "SO-7799": {"item": "会议室投影仪", "qty": 1, "unit_price": 9800, "total": 9800, "po": "PO-2024-0203"},
}

TRIPS = {
    # 行程单号 -> 实际出差天数
    "TRIP-889": {"destination": "上海", "start": "2024-03-11", "end": "2024-03-12", "days": 2},
    "TRIP-902": {"destination": "深圳", "start": "2024-04-02", "end": "2024-04-04", "days": 3},
}

POLICY = {
    "travel": "住宿标准 ≤400 元/晚；住宿夜数不得超过行程单实际天数；交通费需有行程单佐证。",
    "purchase": "必须关联已批准的采购单号，且报销金额不得超过该采购单的批复额度。",
    "entertainment": "人均标准 ≤200 元，需注明招待人数。",
}

HISTORY = {
    "张伟": "上季度报销 3 笔，其中 1 笔（差旅住宿）因超标被驳回。",
    "李娜": "上季度报销 5 笔，全部通过。",
}


@tool
def query_approval(po_number: str) -> str:
    """查询采购审批单的批复额度、申请人和状态。输入采购单号，例如 PO-2024-0156。"""
    r = APPROVALS.get(po_number.strip().upper())
    if not r:
        return f"审批系统中未找到采购单号 {po_number}。"
    return (
        f"采购单 {po_number}：批复额度 {r['approved_amount']} 元，"
        f"申请人 {r['applicant']}，状态 {r['status']}。"
    )


@tool
def query_order(order_no: str) -> str:
    """查询订单系统里的订单明细。输入订单号，例如 SO-7781。"""
    r = ORDERS.get(order_no.strip().upper())
    if not r:
        return f"订单系统中未找到订单号 {order_no}。"
    return (
        f"订单 {order_no}：{r['item']} {r['qty']} 件，单价 {r['unit_price']} 元，"
        f"合计 {r['total']} 元，关联采购单 {r['po']}。"
    )


@tool
def query_trip(trip_no: str) -> str:
    """查询出差行程单的实际起止日期和天数。输入行程单号，例如 TRIP-889。"""
    r = TRIPS.get(trip_no.strip().upper())
    if not r:
        return f"差旅系统中未找到行程单号 {trip_no}。"
    return (
        f"行程单 {trip_no}：目的地 {r['destination']}，"
        f"{r['start']} 至 {r['end']}，共 {r['days']} 天。"
    )


@tool
def query_policy(expense_type: str) -> str:
    """查询某一类报销的合规标准。expense_type 取值：travel / purchase / entertainment。"""
    r = POLICY.get(expense_type.strip().lower())
    if not r:
        return f"未找到类别 {expense_type} 的报销标准。可选值：travel / purchase / entertainment。"
    return f"【{expense_type}】报销标准：{r}"


@tool
def query_history(employee: str) -> str:
    """查询某位员工的历史报销记录。输入员工姓名。"""
    r = HISTORY.get(employee.strip())
    if not r:
        return f"未找到员工 {employee} 的历史报销记录。"
    return f"{employee} 的历史报销：{r}"


# 自主版能用到的全部工具 —— 注意：它的能力边界是这里（人）定的
TOOLS = [query_approval, query_order, query_trip, query_policy, query_history]


# ══════════════════════════════════════════════════════════════════
#  3. 观测用的计数器 —— 让两版的「代价」可见
# ══════════════════════════════════════════════════════════════════

class Counter(BaseCallbackHandler):
    """挂到 config 上就能自动统计 LLM 调用次数和工具调用明细。"""

    def __init__(self) -> None:
        self.llm_calls = 0
        self.tools: List[str] = []

    def on_llm_start(self, *args, **kwargs) -> None:
        self.llm_calls += 1

    def on_tool_start(self, serialized, input_str, *args, **kwargs) -> None:
        name = (serialized or {}).get("name", "?")
        self.tools.append(name)

    def summary(self) -> str:
        return f"{self.llm_calls} 次 LLM / {len(self.tools)} 次工具"


# ══════════════════════════════════════════════════════════════════
#  4. State —— 报销审核这条流程里要传递的全部数据
# ══════════════════════════════════════════════════════════════════

class ExpenseState(TypedDict, total=False):
    # 输入
    receipt_text: str
    employee: str
    # ① 校验节点写
    is_valid: bool
    invalid_reason: str
    # ② 分类节点写
    expense_type: str
    amount: float
    # ③ 核对节点写（★ 两版差异就在这一格的内容）
    check_result: Dict[str, Any]
    # ④ 生成意见节点写
    opinion: str
    approver: str


# ══════════════════════════════════════════════════════════════════
#  5. 两版【共用】的节点
# ══════════════════════════════════════════════════════════════════

def validate_receipt(state: ExpenseState) -> Dict[str, Any]:
    """① 单据有效性校验。"""
    r = llm_json(f"""判断这张报销单是否有效（有效 = 内容清晰、属于本公司报销范围、能看出报销事项）。
无效的例子：空白、无关附件、看不清、纯闲聊。

报销单内容：
{state['receipt_text']}

输出 JSON：{{"valid": true/false, "reason": "无效时说明原因，有效则为空字符串"}}""")
    return {
        "is_valid": bool(r.get("valid", False)),
        "invalid_reason": str(r.get("reason", "")),
    }


def classify_expense(state: ExpenseState) -> Dict[str, Any]:
    """② 判断报销类别 + 抽取金额。"""
    r = llm_json(f"""判断这张报销单的类别并抽取总金额。

类别只能是以下之一：
- travel（差旅）
- purchase（采购）
- entertainment（招待）

报销单内容：
{state['receipt_text']}

输出 JSON：{{"type": "travel/purchase/entertainment", "amount": 数字}}""")
    etype = str(r.get("type", "unknown")).strip().lower()
    if etype not in ("travel", "purchase", "entertainment"):
        etype = "unknown"
    try:
        amount = float(r.get("amount", 0) or 0)
    except (TypeError, ValueError):
        amount = 0.0
    return {"expense_type": etype, "amount": amount}


def draft_opinion(state: ExpenseState) -> Dict[str, Any]:
    """④ 综合核对结果，生成审批意见。"""
    r = llm_json(f"""你是财务审核员，请根据下面的核对结果给出审批意见。

报销类别：{state.get('expense_type')}
报销金额：{state.get('amount')} 元
核对结果：{json.dumps(state.get('check_result', {}), ensure_ascii=False)}

【硬性规则】
- 只要核对结果里 compliant 为 false，就必须给出"驳回"或"需补充材料"，不得给出"通过"。
- 若核对结果里列出了 issues 但 compliant 为 true，意见中也要把这些疑点提示出来。

输出 JSON：{{"opinion": "审批意见，2-3 句，包含结论和理由"}}""")
    return {"opinion": str(r.get("opinion", r.get("_raw", "")))}


def notify_director(state: ExpenseState) -> Dict[str, Any]:
    return {"approver": "总监审批（金额 > 5000）"}


def notify_manager(state: ExpenseState) -> Dict[str, Any]:
    return {"approver": "主管审批（金额 ≤ 5000）"}


# ══════════════════════════════════════════════════════════════════
#  6. 路由函数 —— 判据全部来自 State
# ══════════════════════════════════════════════════════════════════

def route_after_validate(state: ExpenseState) -> str:
    return "classify_expense" if state.get("is_valid") else "reject"


def route_by_amount(state: ExpenseState) -> str:
    return "director" if float(state.get("amount", 0) or 0) > 5000 else "manager"


# ══════════════════════════════════════════════════════════════════
#  7. 组装图 —— ★ 唯一的外部输入就是 check_fn
# ══════════════════════════════════════════════════════════════════

def build_graph(check_fn):
    """
    两版共用这一个函数。
    check_fn 是第 3 个节点「核对」的实现 —— 换掉它，图的形状完全不变。
    """
    w = StateGraph(ExpenseState)

    w.add_node("validate_receipt", validate_receipt)
    w.add_node("classify_expense", classify_expense)
    w.add_node("check_expense", check_fn)          # ← ← ← 唯一的差异点
    w.add_node("draft_opinion", draft_opinion)
    w.add_node("notify_director", notify_director)
    w.add_node("notify_manager", notify_manager)

    w.set_entry_point("validate_receipt")

    # 分叉①：无效单据直接结束，不浪费时间
    w.add_conditional_edges("validate_receipt", route_after_validate, {
        "classify_expense": "classify_expense",
        "reject": END,
    })

    w.add_edge("classify_expense", "check_expense")
    w.add_edge("check_expense", "draft_opinion")

    # 分叉②：按金额决定审批人
    w.add_conditional_edges("draft_opinion", route_by_amount, {
        "director": "notify_director",
        "manager": "notify_manager",
    })
    w.add_edge("notify_director", END)
    w.add_edge("notify_manager", END)

    return w.compile()


# ══════════════════════════════════════════════════════════════════
#  8. 测试数据
# ══════════════════════════════════════════════════════════════════

CASES = [
    {
        "id": "单据 1 · 差旅",
        "trap": "文本里看不出问题：行程单是 2 天，但住宿报了 3 晚；且单价超标准",
        "receipt_text": """报销事由：上海客户拜访
出差行程单号：TRIP-889
住宿发票：3 晚，合计 2400 元
交通发票：1200 元
报销合计：3600 元""",
        "employee": "张伟",
    },
    {
        "id": "单据 2 · 采购",
        "trap": "文本里看不出问题：报销 8600 元，但审批单批复额度只有 5000 元",
        "receipt_text": """报销事由：采购服务器硬盘
采购单号：PO-2024-0156
订单号：SO-7781
报销金额：8600 元""",
        "employee": "李娜",
    },
    {
        "id": "单据 3 · 招待",
        "trap": "没有坑：人均 200 元正好达标，单据信息自足",
        "receipt_text": """报销事由：客户招待 4 人
招待费用：800 元
人均：200 元""",
        "employee": "李娜",
    },
]


def check_env() -> None:
    """跑之前先确认 key 配好了。"""
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("[错误] 没有找到 DEEPSEEK_API_KEY。")
        print("       请把 .env.template 复制成 .env 并填入你的 key。")
        raise SystemExit(1)
