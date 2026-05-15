# benchmark_harness.py
# Purpose: Run identical prompts across multiple LLMs and measure
# performance across 4 dimensions that matter for PM decisions.
# Output: A formatted table + cost analysis you can screenshot for portfolio.

import os
from pathlib import Path

from dotenv import load_dotenv

# Resolve .env from the script location so keys load even when cwd is week2/day4.
for _d in [Path(__file__).resolve().parent, *Path(__file__).resolve().parent.parents]:
    _env = _d / ".env"
    if _env.is_file():
        load_dotenv(_env)
        break

import anthropic
import openai
import time
import json
from tabulate import tabulate  # pip install tabulate

# ── Pricing constants (verify at docs before production use) ─────────────────
# Format: (cost per 1M input tokens, cost per 1M output tokens)

PRICING = {
    "claude-sonnet-4":  (3.00, 15.00),
    "gpt-4o":           (2.50, 10.00),
}

# ── Cost calculator ──────────────────────────────────────────────────────────

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Returns cost in USD for a single API call.
    
    Why this matters for PMs: At scale, small per-call differences
    become enormous budget line items. 
    Example: $0.001 difference × 50M daily calls = $50K/day = $18M/year
    """
    if model not in PRICING:
        return 0.0
    
    input_price, output_price = PRICING[model]
    
    # Divide by 1M because prices are quoted per million tokens
    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price
    
    return input_cost + output_cost

# ── Model callers (reusing pattern from model_basics.py) ────────────────────

def call_claude(prompt: str, system: str = "") -> dict:
    client = anthropic.Anthropic()
    start = time.time()
    
    kwargs = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}]
    }
    # Only add system prompt if one was provided
    if system:
        kwargs["system"] = system
    
    message = client.messages.create(**kwargs)
    elapsed_ms = (time.time() - start) * 1000
    
    return {
        "model": "claude-sonnet-4",
        "response": message.content[0].text,
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "latency_ms": round(elapsed_ms, 1),
        "cost_usd": calculate_cost("claude-sonnet-4",
                                    message.usage.input_tokens,
                                    message.usage.output_tokens)
    }

def call_gpt4(prompt: str, system: str = "") -> dict:
    client = openai.OpenAI()
    start = time.time()
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=messages
    )
    elapsed_ms = (time.time() - start) * 1000
    
    return {
        "model": "gpt-4o",
        "response": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "latency_ms": round(elapsed_ms, 1),
        "cost_usd": calculate_cost("gpt-4o",
                                    response.usage.prompt_tokens,
                                    response.usage.completion_tokens)
    }

# ── The benchmark test suite ─────────────────────────────────────────────────
# Each test probes a different capability dimension.
# As an AI PM, you'd design these tests around YOUR product's actual use cases.

BENCHMARK_TESTS = [
    {
        "id": "instruction_following",
        "name": "Instruction Following",
        "prompt": "List exactly 3 benefits of on-device AI processing. Use exactly this format:\n1. [benefit]\n2. [benefit]\n3. [benefit]\nDo not add any introduction or conclusion.",
        "system": "",
        # What we're testing: Does the model follow precise formatting instructions?
        # Why it matters: Feature reliability — if you say "return JSON", does it?
        "eval_hint": "Check: exactly 3 items, numbered format, no extra text"
    },
    {
        "id": "context_fidelity",
        "name": "Context Fidelity (RAG simulation)",
        "prompt": """Using ONLY the information below, answer: What is Apple's primary reason for on-device processing?

CONTEXT:
Apple processes user data on-device primarily to ensure that personal information never leaves the user's device. This approach means Apple's servers never see the raw data, making it impossible for Apple to be compelled to hand over user communications even if legally requested.

QUESTION: What is Apple's primary reason for on-device processing?""",
        "system": "",
        # What we're testing: Does the model use the provided context faithfully,
        # or does it add outside knowledge and potentially hallucinate?
        "eval_hint": "Check: answer grounded in context, no hallucinated additions"
    },
    {
        "id": "structured_output",
        "name": "Structured Output (JSON)",
        "prompt": 'Return a JSON object with exactly these fields: {"model_name": string, "best_use_case": string, "latency_tier": "fast|medium|slow"}. Fill in for yourself. Return only valid JSON, no markdown.',
        "system": "You are a helpful assistant that returns only valid JSON.",
        # What we're testing: Can the model reliably produce structured output?
        # Why it matters: Most production AI features consume JSON, not prose.
        "eval_hint": "Check: valid JSON, all 3 fields present, correct data types"
    },
    {
        "id": "conciseness",
        "name": "Conciseness Under Constraint",
        "prompt": "Explain how Apple Intelligence works. Maximum 50 words.",
        "system": "",
        # What we're testing: Does the model respect length constraints?
        # Why it matters: Mobile UI has limited space; verbosity breaks layouts.
        "eval_hint": "Check: word count ≤50, substantive content included"
    }
]

# ── Scoring function ─────────────────────────────────────────────────────────

def score_response(test: dict, result: dict) -> dict:
    """
    Simple manual scoring. In production evals (Week 3), this becomes automated.
    For now, we're flagging what to look for — you evaluate by reading the output.
    """
    response = result["response"]
    
    scores = {}
    
    if test["id"] == "instruction_following":
        # Count numbered items
        lines = [l.strip() for l in response.split("\n") if l.strip()]
        numbered = [l for l in lines if l[:2] in ["1.", "2.", "3."]]
        scores["format_correct"] = len(numbered) == 3
        scores["no_extra_text"] = len(lines) <= 4  # 3 items + maybe blank
        
    elif test["id"] == "structured_output":
        # Try to parse as JSON
        try:
            parsed = json.loads(response.strip())
            scores["valid_json"] = True
            scores["has_all_fields"] = all(
                k in parsed for k in ["model_name", "best_use_case", "latency_tier"]
            )
        except json.JSONDecodeError:
            scores["valid_json"] = False
            scores["has_all_fields"] = False
            
    elif test["id"] == "conciseness":
        word_count = len(response.split())
        scores["word_count"] = word_count
        scores["within_limit"] = word_count <= 50
        
    return scores

# ── Main benchmark runner ────────────────────────────────────────────────────

def run_benchmark():
    missing = [
        name
        for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY")
        if not os.environ.get(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing API key(s): "
            + ", ".join(missing)
            + ". Add them to the repo-root .env (ANTHROPIC_API_KEY, OPENAI_API_KEY) "
            "or export them in your shell."
        )

    print("\n" + "="*60)
    print("AI MODEL BENCHMARK HARNESS")
    print("Running 4 tests × 2 models = 8 API calls")
    print("="*60 + "\n")
    
    all_results = []
    summary_rows = []
    
    for test in BENCHMARK_TESTS:
        print(f"\n📋 Test: {test['name']}")
        print(f"   Eval hint: {test['eval_hint']}")
        print("-" * 50)
        
        for caller_name, caller_fn in [("Claude Sonnet 4", call_claude), 
                                        ("GPT-4o", call_gpt4)]:
            print(f"\n  🤖 {caller_name}:")
            
            result = caller_fn(test["prompt"], test.get("system", ""))
            scores = score_response(test, result)
            
            # Print response (truncated for readability)
            response_preview = result["response"][:200]
            if len(result["response"]) > 200:
                response_preview += "..."
            print(f"  Response: {response_preview}")
            print(f"  Latency: {result['latency_ms']}ms | "
                  f"Tokens: {result['input_tokens']}in/{result['output_tokens']}out | "
                  f"Cost: ${result['cost_usd']:.6f}")
            if scores:
                print(f"  Auto-scores: {scores}")
            
            # Collect for summary table
            summary_rows.append({
                "Test": test["name"][:25],
                "Model": result["model"],
                "Latency(ms)": result["latency_ms"],
                "In Tokens": result["input_tokens"],
                "Out Tokens": result["output_tokens"],
                "Cost($)": f"{result['cost_usd']:.6f}",
                "Scores": str(scores) if scores else "manual review"
            })
            
            all_results.append({
                "test": test["id"],
                "model": result["model"],
                "result": result,
                "scores": scores
            })
    
    # ── Summary table ────────────────────────────────────────────────────────
    print("\n\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    
    # Group by model for cost totals
    claude_rows = [r for r in all_results if "claude" in r["model"]]
    gpt_rows = [r for r in all_results if "gpt" in r["model"]]
    
    claude_total_cost = sum(r["result"]["cost_usd"] for r in claude_rows)
    gpt_total_cost = sum(r["result"]["cost_usd"] for r in gpt_rows)
    
    claude_avg_latency = sum(r["result"]["latency_ms"] for r in claude_rows) / len(claude_rows)
    gpt_avg_latency = sum(r["result"]["latency_ms"] for r in gpt_rows) / len(gpt_rows)
    
    print(tabulate(
        summary_rows,
        headers="keys",
        tablefmt="rounded_outline"
    ))
    
    print(f"\n📊 COST TOTALS (for these 4 test calls):")
    print(f"   Claude Sonnet 4: ${claude_total_cost:.6f}")
    print(f"   GPT-4o:          ${gpt_total_cost:.6f}")
    
    print(f"\n⏱️  AVERAGE LATENCY:")
    print(f"   Claude Sonnet 4: {claude_avg_latency:.0f}ms")
    print(f"   GPT-4o:          {gpt_avg_latency:.0f}ms")
    
    # ── Scale projection ─────────────────────────────────────────────────────
    # This is the PM-critical section: what do these numbers mean at Apple scale?
    print(f"\n🔭 SCALE PROJECTION (Apple-level: 50M requests/day):")
    
    for model_name, total_cost, rows in [
        ("Claude Sonnet 4", claude_total_cost, claude_rows),
        ("GPT-4o", gpt_total_cost, gpt_rows)
    ]:
        # Average cost per call from our test
        avg_cost_per_call = total_cost / len(rows)
        
        daily_cost = avg_cost_per_call * 50_000_000
        monthly_cost = daily_cost * 30
        annual_cost = daily_cost * 365
        
        print(f"\n   {model_name}:")
        print(f"   Avg cost/call: ${avg_cost_per_call:.6f}")
        print(f"   Daily (50M req): ${daily_cost:,.2f}")
        print(f"   Monthly:         ${monthly_cost:,.0f}")
        print(f"   Annual:          ${annual_cost:,.0f}")
    
    print("\n✅ Benchmark complete. Review responses above for qualitative eval.")
    
    return all_results

if __name__ == "__main__":
    run_benchmark()