# eval_runner.py
# Purpose: Execute the eval suite from Day 1 against a real model.
# For each test case, call Claude with a PRD summarizer prompt and
# check the assertion — automatically for deterministic evals,
# via a judge call for model-graded evals.
# Output: structured results dict, printed summary, and a JSON results file.

import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv

for _d in [Path(__file__).resolve().parent, *Path(__file__).resolve().parent.parents]:
    _env = _d / ".env"
    if _env.is_file():
        load_dotenv(_env)
        break

import anthropic

_DIR = Path(__file__).resolve().parent
_TEST_CASES_PATH = _DIR.parent / "day1" / "test_cases.json"
_RESULTS_PATH = _DIR / "eval_results.json"

# ── Pricing (verify at docs before production use) ───────────────────────────
# claude-sonnet-4: $3.00/$15.00 per 1M tokens
_INPUT_PRICE_PER_M = 3.00
_OUTPUT_PRICE_PER_M = 15.00

SYSTEM_PROMPT = (
    "You are a product summary assistant. "
    "Given a Product Requirements Document (PRD), write a summary in exactly 3 sentences. "
    "Do not use bullet points or numbered lists. "
    "Be concise and capture the most important information."
)

MODEL = "claude-sonnet-4-20250514"


def _cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1_000_000) * _INPUT_PRICE_PER_M + \
           (output_tokens / 1_000_000) * _OUTPUT_PRICE_PER_M


def call_model(user_input: str) -> dict:
    client = anthropic.Anthropic()
    start = time.time()
    message = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_input}]
    )
    elapsed_ms = (time.time() - start) * 1000
    return {
        "response": message.content[0].text,
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "latency_ms": round(elapsed_ms, 1),
        "cost_usd": _cost_usd(message.usage.input_tokens, message.usage.output_tokens),
    }


# ── Deterministic assertion checker ─────────────────────────────────────────

def _sentence_count(text: str) -> int:
    # Split on sentence-ending punctuation followed by whitespace or end-of-string.
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return len([s for s in sentences if s])


def check_deterministic(assertion_str: str, output: str) -> tuple[bool, str]:
    """
    Evaluate a plain-English assertion against the model output.
    Returns (passed: bool, detail: str).
    """
    a = assertion_str.lower()

    # TC001: output length <= 400 AND no bullet points
    if "output length <= 400" in a and "bullet points" in a:
        length_ok = len(output) <= 400
        no_bullets = not bool(re.search(r"^\s*[-•*]", output, re.MULTILINE))
        passed = length_ok and no_bullets
        return passed, f"len={len(output)} (≤400: {length_ok}), no_bullets={no_bullets}"

    # TC002: sentence_count == 3
    if "sentence_count" in a and "== 3" in a:
        count = _sentence_count(output)
        return count == 3, f"sentence_count={count}"

    # TC004: not empty AND length >= 50
    if "not empty" in a and "length >= 50" in a:
        not_empty = bool(output.strip())
        long_enough = len(output) >= 50
        passed = not_empty and long_enough
        return passed, f"not_empty={not_empty}, len={len(output)} (≥50: {long_enough})"

    # TC005: does NOT contain a specific string
    if "does not contain" in a:
        # Extract the quoted string to search for
        match = re.search(r"'([^']+)'", assertion_str)
        if match:
            forbidden = match.group(1)
            passed = forbidden.lower() not in output.lower()
            return passed, f"contains '{forbidden}': {not passed}"

    return False, f"Unrecognised assertion pattern: {assertion_str}"


# ── Model-graded assertion checker ───────────────────────────────────────────

def check_model_graded(assertion_str: str, input_text: str, output: str) -> tuple[bool, str]:
    """
    Use Claude as a judge. Asks for a score 1-5 and passes if >= 4.
    """
    # Extract the evaluation question from the assertion string
    match = re.search(r"'([^']+)'", assertion_str)
    eval_question = match.group(1) if match else "Is this a good summary?"

    client = anthropic.Anthropic()
    judge_prompt = (
        f"You are an expert evaluator. Score the following model output on a scale of 1-5.\n\n"
        f"Evaluation criterion: {eval_question}\n\n"
        f"Original input:\n{input_text}\n\n"
        f"Model output:\n{output}\n\n"
        f"Respond with only a single integer between 1 and 5. No explanation."
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=10,
        messages=[{"role": "user", "content": judge_prompt}]
    )
    raw = message.content[0].text.strip()
    try:
        score = int(re.search(r"\d", raw).group())
    except (AttributeError, ValueError):
        return False, f"Judge returned unparseable score: '{raw}'"

    passed = score >= 4
    return passed, f"judge_score={score}/5 (threshold=4)"


# ── Main runner ───────────────────────────────────────────────────────────────

def run_evals(test_cases: list[dict]) -> list[dict]:
    results = []
    total_cost = 0.0

    print(f"\n{'='*60}")
    print("  PRD SUMMARIZER — AUTOMATED EVAL SUITE")
    print(f"  {len(test_cases)} test cases | model: claude-sonnet-4")
    print(f"{'='*60}\n")

    for tc in test_cases:
        print(f"  [{tc['id']}] {tc['description']}")

        call = call_model(tc["input"])
        total_cost += call["cost_usd"]

        if tc["eval_type"] == "deterministic":
            passed, detail = check_deterministic(tc["assertion"], call["response"])
        elif tc["eval_type"] == "model_graded":
            passed, detail = check_model_graded(tc["assertion"], tc["input"], call["response"])
        else:
            passed, detail = False, f"Unknown eval_type: {tc['eval_type']}"

        status = "PASS" if passed else "FAIL"
        print(f"  {status} | {detail}")
        print(f"  Latency: {call['latency_ms']}ms | Cost: ${call['cost_usd']:.6f}")
        print(f"  Output preview: {call['response'][:120].replace(chr(10), ' ')}...")
        print()

        results.append({
            "id": tc["id"],
            "description": tc["description"],
            "eval_type": tc["eval_type"],
            "passed": passed,
            "detail": detail,
            "latency_ms": call["latency_ms"],
            "cost_usd": call["cost_usd"],
            "response": call["response"],
        })

    passed_count = sum(1 for r in results if r["passed"])
    print(f"{'─'*60}")
    print(f"  Result: {passed_count}/{len(results)} passed")
    print(f"  Total cost: ${total_cost:.6f}")
    print(f"{'─'*60}\n")

    return results


if __name__ == "__main__":
    missing = [k for k in ("ANTHROPIC_API_KEY",) if not os.environ.get(k)]
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}. Add to .env at repo root.")

    with open(_TEST_CASES_PATH) as f:
        test_cases = json.load(f)

    results = run_evals(test_cases)

    with open(_RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Results saved to {_RESULTS_PATH.relative_to(_DIR.parent.parent)}")
