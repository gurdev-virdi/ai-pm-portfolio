# eval_report.py
# Purpose: Read eval_results.json (produced by eval_runner.py) and render a
# formatted markdown report. Run this after eval_runner.py completes.
# Output: eval_report.md — a screenshot-ready summary for your portfolio.

import json
from datetime import date
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RESULTS_PATH = _DIR / "eval_results.json"
_REPORT_PATH = _DIR / "eval_report.md"

STATUS = {True: "PASS", False: "FAIL"}
ICON   = {True: "✅",    False: "❌"}


def _pass_rate(results: list[dict]) -> str:
    n = len(results)
    p = sum(1 for r in results if r["passed"])
    pct = (p / n * 100) if n else 0
    return f"{p}/{n} ({pct:.0f}%)"


def _total_cost(results: list[dict]) -> float:
    return sum(r["cost_usd"] for r in results)


def _avg_latency(results: list[dict]) -> float:
    if not results:
        return 0.0
    return sum(r["latency_ms"] for r in results) / len(results)


def generate_report(results: list[dict]) -> str:
    today = date.today().isoformat()
    passed = sum(1 for r in results if r["passed"])
    total  = len(results)
    pct    = (passed / total * 100) if total else 0

    lines = [
        f"# PRD Summarizer — Eval Report",
        f"",
        f"**Date:** {today}  ",
        f"**Model:** claude-sonnet-4  ",
        f"**Pass rate:** {passed}/{total} ({pct:.0f}%)  ",
        f"**Total cost:** ${_total_cost(results):.6f}  ",
        f"**Avg latency:** {_avg_latency(results):.0f} ms  ",
        f"",
        f"---",
        f"",
        f"## Results by Test Case",
        f"",
        f"| ID | Type | Result | Detail | Latency |",
        f"|---|---|---|---|---|",
    ]

    for r in results:
        icon   = ICON[r["passed"]]
        status = STATUS[r["passed"]]
        lines.append(
            f"| {r['id']} | {r['eval_type']} | {icon} {status} "
            f"| {r['detail']} | {r['latency_ms']} ms |"
        )

    lines += [
        f"",
        f"---",
        f"",
        f"## Detailed Outputs",
        f"",
    ]

    for r in results:
        icon = ICON[r["passed"]]
        lines += [
            f"### {r['id']} — {r['description']}",
            f"",
            f"**Type:** `{r['eval_type']}` | **Result:** {icon} {STATUS[r['passed']]}  ",
            f"**Assertion detail:** {r['detail']}  ",
            f"**Cost:** ${r['cost_usd']:.6f} | **Latency:** {r['latency_ms']} ms  ",
            f"",
            f"**Model output:**",
            f"",
            f"> {r['response'].strip().replace(chr(10), '  ').replace(chr(13), '')}",
            f"",
        ]

    lines += [
        f"---",
        f"",
        f"## PM Takeaways",
        f"",
        f"- **Deterministic evals** (length, format, injection resistance) run in milliseconds "
        f"with zero extra cost — run them on every deployment.",
        f"- **Model-graded evals** add one extra API call per case (~$0.000015 each) "
        f"but catch quality regressions that rules cannot.",
        f"- At 99% pass rate threshold on {total} cases, any single failure blocks the release — "
        f"calibrate thresholds to your product's risk tolerance.",
        f"- Track cost-per-eval over time; rising costs signal prompt or model changes "
        f"that need review.",
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    if not _RESULTS_PATH.exists():
        raise SystemExit(
            f"{_RESULTS_PATH.name} not found. Run eval_runner.py first."
        )

    with open(_RESULTS_PATH) as f:
        results = json.load(f)

    report = generate_report(results)

    with open(_REPORT_PATH, "w") as f:
        f.write(report)

    print(f"Report written to {_REPORT_PATH.relative_to(_DIR.parent.parent)}")
    print(f"Pass rate: {_pass_rate(results)}")
    print(f"Total cost: ${_total_cost(results):.6f}")
