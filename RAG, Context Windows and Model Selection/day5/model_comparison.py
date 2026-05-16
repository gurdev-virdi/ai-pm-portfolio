# model_comparison.py
# Runs the same prompt through multiple models and measures
# capability, cost, and latency side-by-side

import os
import time
import anthropic
import openai
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

# ── Clients ──────────────────────────────────────────────────────────────────
# Each client talks to a different provider's API
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client    = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── Pricing (as of early 2026, per 1M tokens) ────────────────────────────────
# These are the numbers you cite in interviews. Update them periodically.
PRICING = {
    "claude-3-5-haiku-20241022":  {"input": 0.80,  "output": 4.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00,  "output": 15.00},
    "gpt-4o-mini":                {"input": 0.15,  "output": 0.60},
    "gpt-4o":                     {"input": 2.50,  "output": 10.00},
}

# ── Core runner ───────────────────────────────────────────────────────────────
def run_claude(model: str, prompt: str, system: str = "") -> dict:
    """
    Send a prompt to a Claude model and capture timing + token usage.
    Returns a dict so we can compare results uniformly across providers.
    """
    start = time.time()

    response = anthropic_client.messages.create(
        model=model,
        max_tokens=500,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )

    elapsed = time.time() - start

    # response.usage gives us exact token counts — crucial for cost math
    input_tokens  = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    # Cost calculation: tokens used / 1M * price per 1M
    price    = PRICING.get(model, {"input": 0, "output": 0})
    cost_usd = (input_tokens / 1_000_000 * price["input"] +
                output_tokens / 1_000_000 * price["output"])

    return {
        "model":         model,
        "provider":      "Anthropic",
        "response":      response.content[0].text,
        "input_tokens":  input_tokens,
        "output_tokens": output_tokens,
        "latency_s":     round(elapsed, 2),
        "cost_usd":      round(cost_usd, 6),
    }


def run_openai(model: str, prompt: str, system: str = "") -> dict:
    """
    Same structure as run_claude — uniform interface means easy comparison.
    OpenAI uses the 'choices' structure rather than 'content'.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    start = time.time()

    response = openai_client.chat.completions.create(
        model=model,
        max_tokens=500,
        messages=messages
    )

    elapsed = time.time() - start

    input_tokens  = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    price    = PRICING.get(model, {"input": 0, "output": 0})
    cost_usd = (input_tokens / 1_000_000 * price["input"] +
                output_tokens / 1_000_000 * price["output"])

    return {
        "model":         model,
        "provider":      "OpenAI",
        "response":      response.choices[0].message.content,
        "input_tokens":  input_tokens,
        "output_tokens": output_tokens,
        "latency_s":     round(elapsed, 2),
        "cost_usd":      round(cost_usd, 6),
    }


# ── Benchmark runner ──────────────────────────────────────────────────────────
def run_benchmark(prompts: list[dict]) -> list[dict]:
    """
    Run every prompt through every model.
    prompts = [{"name": "...", "system": "...", "user": "..."}]
    Returns flat list of all results for tabulation.
    """
    models_to_test = [
        ("claude", "claude-3-5-haiku-20241022"),
        ("claude", "claude-3-5-sonnet-20241022"),
        ("openai", "gpt-4o-mini"),
        ("openai", "gpt-4o"),
    ]

    all_results = []

    for prompt_config in prompts:
        print(f"\n📋 Testing prompt: '{prompt_config['name']}'")

        for provider, model in models_to_test:
            print(f"   → {model}...", end="", flush=True)

            try:
                if provider == "claude":
                    result = run_claude(model, prompt_config["user"],
                                        prompt_config.get("system", ""))
                else:
                    result = run_openai(model, prompt_config["user"],
                                        prompt_config.get("system", ""))

                result["prompt_name"] = prompt_config["name"]
                all_results.append(result)
                print(f" {result['latency_s']}s | ${result['cost_usd']}")

            except Exception as e:
                print(f" ERROR: {e}")

    return all_results


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Three prompts that test different capability dimensions
    # As a PM, you want to evaluate the tasks YOUR product actually needs
    test_prompts = [
        {
            "name": "Simple factual",
            "system": "You are a helpful assistant. Be concise.",
            "user": "What is the capital of France? Answer in one sentence."
        },
        {
            "name": "Reasoning",
            "system": "You are a helpful assistant.",
            "user": (
                "A user's iPhone has 2GB free. They want to run an on-device "
                "AI model. A 7B parameter model in 4-bit quantization needs "
                "~4GB. A 1B model needs ~0.7GB. What should they do, and why?"
            )
        },
        {
            "name": "Structured output",
            "system": "You are a helpful assistant. Always respond in valid JSON.",
            "user": (
                "List 3 tradeoffs between on-device and cloud AI. "
                "Return as JSON: {tradeoffs: [{dimension, on_device, cloud}]}"
            )
        },
    ]

    results = run_benchmark(test_prompts)

    # ── Summary table ─────────────────────────────────────────────────────────
    print("\n\n" + "="*70)
    print("BENCHMARK RESULTS")
    print("="*70)

    table_data = [
        [
            r["prompt_name"],
            r["model"].split("-")[0] + "-" + r["model"].split("-")[-1],
            f"{r['latency_s']}s",
            f"${r['cost_usd']}",
            r["input_tokens"] + r["output_tokens"],
        ]
        for r in results
    ]

    print(tabulate(
        table_data,
        headers=["Prompt", "Model", "Latency", "Cost/call", "Total tokens"],
        tablefmt="grid"
    ))

    # ── Cost projection ───────────────────────────────────────────────────────
    # This is the PM math that matters: what does this cost at scale?
    print("\n\n" + "="*70)
    print("COST AT SCALE (for the 'Reasoning' prompt)")
    print("="*70)

    reasoning_results = [r for r in results if r["prompt_name"] == "Reasoning"]

    scale_table = []
    for r in reasoning_results:
        cost_per_call = r["cost_usd"]
        scale_table.append([
            r["model"],
            f"${cost_per_call:.6f}",
            f"${cost_per_call * 1_000:.4f}",       # 1K calls/day
            f"${cost_per_call * 100_000:.2f}",      # 100K calls/day
            f"${cost_per_call * 1_000_000:.2f}",    # 1M calls/day
        ])

    print(tabulate(
        scale_table,
        headers=["Model", "Per call", "1K/day", "100K/day", "1M/day"],
        tablefmt="grid"
    ))

    print("\n✅ Benchmark complete. Review outputs above.")