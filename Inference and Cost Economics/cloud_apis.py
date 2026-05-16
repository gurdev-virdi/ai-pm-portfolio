import os
import time
from dotenv import load_dotenv
import anthropic
import openai

load_dotenv()

CLAUDE_HAIKU  = "claude-haiku-4-5-20251001"
CLAUDE_SONNET = "claude-sonnet-4-6"
CLAUDE_OPUS   = "claude-opus-4-6"
GPT_MINI      = "gpt-4o-mini"
GPT_4O        = "gpt-4o"

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
gpt = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# $ per million tokens (input, output). Update when models/pricing change.
PRICING = {
    CLAUDE_HAIKU:  (0.80,  4.00),
    CLAUDE_SONNET: (3.00, 15.00),
    CLAUDE_OPUS:   (5.00, 25.00),
    GPT_MINI:      (0.15,  0.60),
    GPT_4O:        (2.50, 10.00),
    "llama-3.2-local": (0.00, 0.00),
}

def call_claude(prompt: str, model: str = CLAUDE_HAIKU) -> dict:
    start = time.time()
    response = claude.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    latency_ms = (time.time() - start) * 1000
    return {
        "text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "latency_ms": round(latency_ms),
        "model": model
    }

def call_gpt(prompt: str, model: str = GPT_MINI) -> dict:
    start = time.time()
    response = gpt.chat.completions.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    latency_ms = (time.time() - start) * 1000
    return {
        "text": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "latency_ms": round(latency_ms),
        "model": model
    }

def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    if model not in PRICING:
        raise ValueError(f"Unknown model: {model}. Add it to PRICING dict.")
    input_price, output_price = PRICING[model]
    input_cost  = (input_tokens  / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price
    return input_cost + output_cost

def model_comparison_report(prompt: str):
    print("\n" + "="*60)
    print("MODEL COMPARISON REPORT")
    print("="*60)
    print(f"Prompt: '{prompt[:60]}...'" if len(prompt) > 60 else f"Prompt: '{prompt}'")
    print()

    results = []

    try:
        r = call_claude(prompt, CLAUDE_HAIKU)
        r["cost_per_call"] = calculate_cost(r["input_tokens"], r["output_tokens"], r["model"])
        results.append(r)
    except anthropic.APIError as e:
        print(f"Claude failed: {e}\n")
        return

    try:
        r = call_gpt(prompt, GPT_MINI)
        r["cost_per_call"] = calculate_cost(r["input_tokens"], r["output_tokens"], r["model"])
        results.append(r)
    except openai.RateLimitError:
        print("GPT skipped (quota exceeded). Showing Claude-only comparison.\n")
        results.append(None)  # placeholder so indexing below doesn't break
    except openai.APIError as e:
        print(f"GPT failed: {e}\n")
        return

    if len(results) < 2 or results[1] is None:
        # Only Claude (or no GPT result): print single row and skip comparison
        if results and results[0]:
            r = results[0]
            print(f"{'Model':<35} {'Latency':>10} {'Tokens In':>10} {'Tokens Out':>10} {'Cost/Call':>12}")
            print("-" * 82)
            print(f"{r['model']:<35} {r['latency_ms']:>8}ms {r['input_tokens']:>10} {r['output_tokens']:>10} ${r['cost_per_call']:>11.6f}")
        print()
        return

    print(f"{'Model':<35} {'Latency':>10} {'Tokens In':>10} {'Tokens Out':>10} {'Cost/Call':>12} {'Cost/1M calls':>15}")
    print("-" * 95)

    for r in results:
        cost_per_million = r["cost_per_call"] * 1_000_000
        print(
            f"{r['model']:<35} "
            f"{r['latency_ms']:>8}ms "
            f"{r['input_tokens']:>10} "
            f"{r['output_tokens']:>10} "
            f"${r['cost_per_call']:>11.6f} "
            f"${cost_per_million:>14,.2f}"
        )

    print()
    print("SCALE PROJECTIONS (same prompt pattern):")
    print(f"{'Scenario':<30} {'Claude Haiku':>20} {'GPT-4o-mini':>20}")
    print("-" * 72)

    scenarios = [
        ("10K calls/day",     10_000),
        ("100K calls/day",   100_000),
        ("1M calls/day",   1_000_000),
        ("10M calls/day", 10_000_000),
    ]

    for label, volume in scenarios:
        haiku_daily = results[0]["cost_per_call"] * volume
        gpt_daily   = results[1]["cost_per_call"] * volume
        print(f"{label:<30} ${haiku_daily:>18,.2f} ${gpt_daily:>18,.2f}")

    print()
    print("KEY INSIGHT FOR PRODUCT DECISIONS:")
    cheaper = results[0] if results[0]["cost_per_call"] <= results[1]["cost_per_call"] else results[1]
    pricier = results[1] if cheaper == results[0] else results[0]
    savings_pct = ((pricier["cost_per_call"] - cheaper["cost_per_call"]) / pricier["cost_per_call"]) * 100
    print(f"  {cheaper['model']} is {savings_pct:.0f}% cheaper per call.")
    print(f"  At 10M calls/day, that's ${(pricier['cost_per_call'] - cheaper['cost_per_call']) * 10_000_000:,.0f}/day difference.")
    print(f"  That's ${(pricier['cost_per_call'] - cheaper['cost_per_call']) * 10_000_000 * 365:,.0f}/year — a headcount decision.")


# --- Quick API test ---
test_prompt = "In 2 sentences, explain why Apple prioritizes on-device AI."

print("=== Testing APIs ===\n")

try:
    claude_result = call_claude(test_prompt)
    print(f"Claude ({claude_result['model']}):")
    print(f"  Response: {claude_result['text']}")
    print(f"  Tokens: {claude_result['input_tokens']} in / {claude_result['output_tokens']} out")
    print(f"  Latency: {claude_result['latency_ms']}ms\n")
except anthropic.APIError as e:
    print(f"Claude failed: {e}\n")

try:
    gpt_result = call_gpt(test_prompt)
    print(f"GPT ({gpt_result['model']}):")
    print(f"  Response: {gpt_result['text']}")
    print(f"  Tokens: {gpt_result['input_tokens']} in / {gpt_result['output_tokens']} out")
    print(f"  Latency: {gpt_result['latency_ms']}ms")
except openai.RateLimitError:
    print("GPT: Skipped — quota exceeded. Check https://platform.openai.com")
except openai.APIError as e:
    print(f"GPT failed: {e}")

# --- Cost comparison ---
model_comparison_report("Summarize the key privacy benefits of on-device AI processing in 3 bullet points.")