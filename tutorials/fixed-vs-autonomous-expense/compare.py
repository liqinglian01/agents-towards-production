# -*- coding: utf-8 -*-
"""
对比实验 —— 同一批报销单，两版分别审核，把差异摆在一起看。

用法：
    python compare.py

看什么：
    1. 两版分别发现了几个问题（自主版能不能查出单据里没写的东西）
    2. 两版各自花了多少 LLM 调用 / 工具调用 / 时间（自主不是免费的）
"""

import time
from typing import Any, Dict, List

import version_a_fixed
import version_b_hybrid
from expense_common import CASES, check_env

WIDTH = 72


def _wrap(text: str, indent: str = "    ", width: int = WIDTH) -> str:
    """按显示宽度折行（中文算 2 格）。"""
    def dw(s: str) -> int:
        return sum(2 if ord(c) > 0x2E80 else 1 for c in s)

    lines, cur, cur_w = [], "", 0
    for ch in str(text).replace("\n", " "):
        w = dw(ch)
        if cur_w + w > width:
            lines.append(cur)
            cur, cur_w = "", 0
        cur += ch
        cur_w += w
    if cur:
        lines.append(cur)
    return "\n".join(indent + ln for ln in lines) if lines else indent


def _norm_issues(raw: Any) -> List[str]:
    if not raw:
        return []
    if isinstance(raw, str):
        return [raw] if raw.strip() else []
    if isinstance(raw, list):
        return [str(x) for x in raw if str(x).strip()]
    return [str(raw)]


def run(app, case: Dict[str, Any]):
    from expense_common import Counter

    counter = Counter()
    t0 = time.time()
    try:
        result = app.invoke(
            {"receipt_text": case["receipt_text"], "employee": case["employee"]},
            config={"callbacks": [counter]},
        )
        error = None
    except Exception as e:                                    # noqa: BLE001
        result, error = {}, f"{type(e).__name__}: {e}"
    return result, counter, time.time() - t0, error


def show(tag: str, result: Dict[str, Any], counter, elapsed: float, error: str):
    print(f"\n  ── {tag} " + "─" * (WIDTH - len(tag) - 6))
    if error:
        print(f"    [运行出错] {error}")
        return
    cr = result.get("check_result", {}) or {}
    issues = _norm_issues(cr.get("issues"))
    print(f"    合规判定 : {'合规' if cr.get('compliant') else '不合规'}")
    if issues:
        print("    发现的问题 :")
        for it in issues:
            print(_wrap("· " + it, indent="      "))
    else:
        print("    发现的问题 : （无）")
    print(f"    判断依据 :\n{_wrap(cr.get('evidence', ''), indent='      ')}")
    print(f"    审批意见 :\n{_wrap(result.get('opinion', '（无）'), indent='      ')}")
    print(f"    审批人   : {result.get('approver', '（已驳回 / 流程结束）')}")
    cost = f"{counter.llm_calls} 次 LLM / {len(counter.tools)} 次工具 / {elapsed:.1f}s"
    print(f"    代价     : {cost}")
    if counter.tools:
        print(f"    查了     : {', '.join(counter.tools)}")


def main() -> None:
    check_env()

    print("=" * WIDTH)
    print(" 对比实验：固定骨架  vs  固定骨架 + 自主格子".center(WIDTH - 6))
    print("=" * WIDTH)

    rows = []
    for case in CASES:
        print(f"\n\n【{case['id']}】")
        print(f"  埋的坑：{case['trap']}")
        print(f"  报销单内容：\n{_wrap(case['receipt_text'])}")

        res_a, cnt_a, t_a, err_a = run(version_a_fixed.app, case)
        res_b, cnt_b, t_b, err_b = run(version_b_hybrid.app, case)

        show("A · 全固定", res_a, cnt_a, t_a, err_a)
        show("B · 骨架 + 自主格子", res_b, cnt_b, t_b, err_b)

        n_a = len(_norm_issues((res_a.get("check_result") or {}).get("issues")))
        n_b = len(_norm_issues((res_b.get("check_result") or {}).get("issues")))
        delta = n_b - n_a
        if delta > 0:
            verdict = f"B 版多查出 {delta} 个问题"
        elif delta < 0:
            verdict = f"A 版多查出 {-delta} 个问题"
        else:
            verdict = "两版发现的问题数相同"
        cost_ratio = (cnt_b.llm_calls / cnt_a.llm_calls) if cnt_a.llm_calls else 0
        time_ratio = (t_b / t_a) if t_a else 0
        print(f"\n  ▶ 差异：{verdict}")
        print(f"         代价：B/A = {cost_ratio:.1f} 倍 LLM 调用、{time_ratio:.1f} 倍耗时")

        rows.append((case["id"], n_a, n_b, cnt_a, cnt_b, t_a, t_b))

    # ── 汇总 ──
    print("\n\n" + "=" * WIDTH)
    print(" 汇总".center(WIDTH - 6))
    print("=" * WIDTH)
    print(f"  {'单据':<16}{'A 问题数':>9}{'B 问题数':>9}   {'A 代价':<14}{'B 代价':<14}")
    print("  " + "-" * (WIDTH - 4))
    for cid, n_a, n_b, ca, cb, ta, tb in rows:
        a_cost = f"{ca.llm_calls}LLM/{len(ca.tools)}工具"
        b_cost = f"{cb.llm_calls}LLM/{len(cb.tools)}工具"
        print(f"  {cid:<16}{n_a:>9}{n_b:>9}   {a_cost:<14}{b_cost:<14}")

    print("\n  读法：")
    print("   · 单据 1 / 2 —— 问题藏在数据库里，单据文本看不出 → 自主版查得出来，固定版漏掉")
    print("   · 单据 3   —— 信息自足，没有坑 → 两版结论相同，但固定版更快更省")
    print("   · 结论：自主不是免费的，也不是万能的；它的价值在于「去查」的能力")


if __name__ == "__main__":
    main()
