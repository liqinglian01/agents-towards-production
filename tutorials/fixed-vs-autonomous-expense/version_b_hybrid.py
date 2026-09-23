# -*- coding: utf-8 -*-
"""
版本 B · 固定骨架 + 自主格子（自主度 L2）

★ 和版本 A 的唯一区别，就是下面这个 check_expense_autonomous 的函数体。

图的形状、State、其他四个节点、路由规则 —— 全部和 A 版一模一样（共用 expense_common.build_graph）。

变化只有一处：核对这一格内部，从「一次 LLM 调用」换成了
一个 create_react_agent —— 它自己决定去查哪些系统、查几次。

它被关在这一格里：
  · 入口确定 —— 只能读 State
  · 出口确定 —— 只能返回一个 dict 写回 State
  · 边界确定 —— 能用哪些工具由人在这份文件里定（TOOLS）
"""

from typing import Any, Dict

# LangChain V1 把这个预置 Agent 从 langgraph.prebuilt 挪到了 langchain.agents，
# 老名字 create_react_agent 仍可用但会打弃用警告。这里做兼容。
try:
    from langchain.agents import create_agent as create_react_agent
except ImportError:                                    # 老版本
    from langgraph.prebuilt import create_react_agent  # type: ignore

from expense_common import (
    CASES,
    TOOLS,
    Counter,
    _parse_json,
    build_graph,
    check_env,
    get_llm,
)


def check_expense_autonomous(state) -> Dict[str, Any]:
    """③ 核对节点（自主版）—— 内部是一个会自己决定查什么的 ReAct Agent。"""
    agent = create_react_agent(
        model=get_llm(),
        tools=TOOLS,
    )

    result = agent.invoke({
        "messages": [("human", f"""你是财务审核员，请核对下面这张报销单是否合规。

你可以使用工具去查询审批系统、订单系统、差旅系统、报销标准和历史记录。
请自己判断需要查什么 —— 单据上提到单号就一定要去查，
单据上的金额和标准也要去核对。

报销类别：{state.get('expense_type')}
报销金额：{state.get('amount')} 元
报销人：{state.get('employee')}
报销单内容：
{state['receipt_text']}

核对完成后，最后一条消息只输出这个 JSON（不要有其他文字）：
{{
  "compliant": true/false,
  "issues": ["发现的问题，没有则为空数组"],
  "evidence": "你的判断依据，说明查了哪些系统、得到什么结论"
}}""")]
    })

    final_text = result["messages"][-1].content
    parsed = _parse_json(final_text)

    return {
        "check_result": {
            "compliant": bool(parsed.get("compliant", True)),
            "issues": parsed.get("issues", []) or [],
            "evidence": str(parsed.get("evidence", final_text)),
            "mode": "autonomous",
        }
    }


app = build_graph(check_expense_autonomous)


def run_one(case: Dict[str, Any]) -> Dict[str, Any]:
    counter = Counter()
    result = app.invoke(
        {"receipt_text": case["receipt_text"], "employee": case["employee"]},
        config={"callbacks": [counter]},
    )
    result["_counter"] = counter
    return result


if __name__ == "__main__":
    check_env()
    print("=" * 70)
    print("版本 B · 固定骨架 + 自主格子 —— 核对节点 = 一个会自己查系统的 Agent")
    print("=" * 70)
    for case in CASES:
        print(f"\n【{case['id']}】")
        r = run_one(case)
        cr = r.get("check_result", {})
        print(f"  合规判定 : {'合规' if cr.get('compliant') else '不合规'}")
        print(f"  发现的问题: {cr.get('issues') or '（无）'}")
        print(f"  依据     : {cr.get('evidence', '')}")
        print(f"  审批意见 : {r.get('opinion', '')}")
        print(f"  审批人   : {r.get('approver', '（已驳回/结束）')}")
        print(f"  代价     : {r['_counter'].summary()}  查了: {r['_counter'].tools or '（无）'}")
