# -*- coding: utf-8 -*-
"""
版本 A · 全固定骨架（自主度 L1）

「核对」节点只是一次 LLM 调用：把报销单文本丢给模型，让它判断是否合规。
模型只能看到单据上写了什么 —— 它没有能力去查任何东西。

这就是教程里那个「固定流程图」的形态：每一步做什么，全是人写死的。
"""

from typing import Any, Dict

from expense_common import CASES, Counter, build_graph, check_env, llm_json


def check_expense_fixed(state) -> Dict[str, Any]:
    """③ 核对节点（固定版）—— 一次 LLM 调用，无工具。"""
    r = llm_json(f"""你是财务审核员，请核对下面这张报销单是否合规。

【重要】你只能根据报销单本身写的内容来判断，
        不要去假设任何单据上没有的信息。

报销类别：{state.get('expense_type')}
报销金额：{state.get('amount')} 元
报销单内容：
{state['receipt_text']}

输出 JSON：
{{
  "compliant": true/false,
  "issues": ["发现的问题，没有则为空数组"],
  "evidence": "你的判断依据，一句话"
}}""")
    return {
        "check_result": {
            "compliant": bool(r.get("compliant", True)),
            "issues": r.get("issues", []) or [],
            "evidence": str(r.get("evidence", r.get("_raw", ""))),
            "mode": "fixed",
        }
    }


app = build_graph(check_expense_fixed)


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
    print("版本 A · 全固定骨架 —— 核对节点 = 一次 LLM 调用（无工具）")
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
        print(f"  代价     : {r['_counter'].summary()}")
