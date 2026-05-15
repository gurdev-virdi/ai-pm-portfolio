"""
Day 5: Token Economics & Cost Modeling
Purpose: Understand how AI API pricing works and build cost projections
         like a PM who owns a product budget.
"""

import tiktoken

# ============================================================
# PART 1: HOW TOKENIZATION WORKS
# ============================================================
# tiktoken is OpenAI's tokenizer library. It shows exactly how
# text gets split into tokens — the units you're billed for.

# Load the tokenizer used by GPT-4 and GPT-4o
encoder = tiktoken.encoding_for_model("gpt-4o")

# Example texts of increasing complexity
test_texts = [
    "Hello",                                    # Simple word
    "Hello, how are you?",                      # Short sentence
    "The quick brown fox jumps over the lazy dog",  # Classic pangram
    "Retrieval-Augmented Generation (RAG) is a technique that combines "
    "information retrieval with language model generation.",  # Technical text
    "こんにちは世界",                              # Non-English (Japanese: "Hello World")
]

print("=" * 60)
print("TOKENIZATION EXAMPLES")
print("=" * 60)

for text in test_texts:
    tokens = encoder.encode(text)
    print(f"\nText: '{text}'")
    print(f"  Characters: {len(text)}")
    print(f"  Tokens:     {len(tokens)}")
    print(f"  Ratio:      {len(text)/len(tokens):.1f} chars/token")
    # Show the actual token breakdown (decode each token individually)
    token_strings = [encoder.decode([t]) for t in tokens]
    print(f"  Breakdown:  {token_strings}")

# ============================================================
# PART 2: CURRENT API PRICING (February 2026)
# ============================================================
# Every provider charges per token, but input and output have
# different rates. Output tokens cost more because they require
# the model to "think" and generate, not just read.
#
# Prices below are per 1 MILLION tokens (industry standard unit).

PRICING = {
    "gpt-4o": {
        "provider": "OpenAI",
        "input_per_1m": 2.50,       # $ per 1M input tokens
        "output_per_1m": 10.00,     # $ per 1M output tokens
        "context_window": 128_000,  # Max tokens per request
        "notes": "Best balance of quality and cost for most tasks"
    },
    "gpt-4o-mini": {
        "provider": "OpenAI",
        "input_per_1m": 0.15,
        "output_per_1m": 0.60,
        "context_window": 128_000,
        "notes": "Very cheap, good for simple tasks and high-volume use"
    },
    "claude-sonnet-4": {
        "provider": "Anthropic",
        "input_per_1m": 3.00,
        "output_per_1m": 15.00,
        "context_window": 200_000,
        "notes": "Strong reasoning, largest context window"
    },
    "claude-haiku-3.5": {
        "provider": "Anthropic",
        "input_per_1m": 0.80,
        "output_per_1m": 4.00,
        "context_window": 200_000,
        "notes": "Fast and affordable Anthropic option"
    },
    "gemini-2.0-flash": {
        "provider": "Google",
        "input_per_1m": 0.10,
        "output_per_1m": 0.40,
        "context_window": 1_000_000,
        "notes": "Cheapest major model, massive context window"
    },
    "llama-3.2-local": {
        "provider": "Local (Ollama)",
        "input_per_1m": 0.00,
        "output_per_1m": 0.00,
        "context_window": 128_000,
        "notes": "Free but requires local GPU/CPU, slower inference"
    },
}

print("\n" + "=" * 60)
print("MODEL PRICING COMPARISON")
print("=" * 60)
print(f"{'Model':<22} {'Input/1M':>10} {'Output/1M':>10} {'Context':>10}")
print("-" * 55)
for model, info in PRICING.items():
    print(f"{model:<22} ${info['input_per_1m']:>8.2f} ${info['output_per_1m']:>8.2f} "
          f"{info['context_window']:>9,}")

# ============================================================
# PART 3: COST PROJECTION CALCULATOR
# ============================================================
# This is the tool you'd actually use in a product planning meeting.
# "If we launch feature X to Y users, what's the API bill?"

def estimate_cost(
    model: str,
    avg_input_tokens: int,    # Average tokens sent per request
    avg_output_tokens: int,   # Average tokens received per request
    requests_per_user_day: int,  # How often users hit the AI feature
    total_users: int,
    days: int = 30            # Default to monthly projection
) -> dict:
    """
    Calculate projected API costs for a product feature.
    
    This is the kind of analysis a PM presents to leadership when
    proposing an AI feature. You need to know: what does this cost
    at scale, and does the unit economics work?
    """
    pricing = PRICING[model]
    
    # Total requests over the time period
    total_requests = total_users * requests_per_user_day * days
    
    # Total tokens consumed
    total_input_tokens = total_requests * avg_input_tokens
    total_output_tokens = total_requests * avg_output_tokens
    
    # Cost calculation (pricing is per 1M tokens)
    input_cost = (total_input_tokens / 1_000_000) * pricing["input_per_1m"]
    output_cost = (total_output_tokens / 1_000_000) * pricing["output_per_1m"]
    total_cost = input_cost + output_cost
    
    # Per-unit economics (critical for PM planning)
    cost_per_request = total_cost / total_requests if total_requests > 0 else 0
    cost_per_user_month = total_cost / total_users if total_users > 0 else 0
    
    return {
        "model": model,
        "total_requests": total_requests,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "cost_per_request": cost_per_request,
        "cost_per_user_month": cost_per_user_month,
    }


# ============================================================
# SCENARIO: "Smart Reply" feature for a productivity app
# ============================================================
# Imagine you're proposing an AI-powered Smart Reply feature
# (like Apple Intelligence's email suggestions).
# 
# Assumptions:
# - Users trigger it ~5 times/day
# - Input: ~500 tokens (email context + system prompt)
# - Output: ~150 tokens (suggested reply)
# - Target: 1M monthly active users

print("\n" + "=" * 60)
print("SCENARIO: Smart Reply Feature (1M users)")
print("=" * 60)

scenario_params = {
    "avg_input_tokens": 500,
    "avg_output_tokens": 150,
    "requests_per_user_day": 5,
    "total_users": 1_000_000,
    "days": 30,
}

# Compare all models for the same scenario
results = []
for model in PRICING:
    result = estimate_cost(model=model, **scenario_params)
    results.append(result)

# Sort by total cost
results.sort(key=lambda x: x["total_cost"])

print(f"\nAssumptions: {scenario_params['avg_input_tokens']} input tokens, "
      f"{scenario_params['avg_output_tokens']} output tokens, "
      f"{scenario_params['requests_per_user_day']}x/day/user")
print(f"Total monthly requests: {results[0]['total_requests']:,}\n")

print(f"{'Model':<22} {'Monthly Cost':>14} {'$/Request':>12} {'$/User/Mo':>12}")
print("-" * 62)
for r in results:
    print(f"{r['model']:<22} ${r['total_cost']:>12,.2f} "
          f"${r['cost_per_request']:>10.5f} ${r['cost_per_user_month']:>10.4f}")


# ============================================================
# PART 4: COST OPTIMIZATION STRATEGIES
# ============================================================
# A PM's job isn't just calculating cost — it's finding ways
# to reduce it without hurting user experience.

print("\n" + "=" * 60)
print("COST OPTIMIZATION: TIERED MODEL STRATEGY")
print("=" * 60)
print("""
Strategy: Route requests by complexity, not one-model-fits-all.

  Simple queries (60%): → gpt-4o-mini or gemini-flash
    e.g., "Thanks, sounds good!" auto-reply
    
  Medium queries (30%): → gpt-4o or claude-haiku
    e.g., Meeting reschedule reply with context
    
  Complex queries (10%): → claude-sonnet or gpt-4o
    e.g., Detailed project update email
""")

# Calculate blended cost with tiered routing
simple = estimate_cost("gpt-4o-mini", **{**scenario_params, 
    "total_users": int(1_000_000 * 0.6)})
medium = estimate_cost("claude-haiku-3.5", **{**scenario_params, 
    "total_users": int(1_000_000 * 0.3)})
complex_q = estimate_cost("claude-sonnet-4", **{**scenario_params, 
    "total_users": int(1_000_000 * 0.1)})

blended_cost = simple["total_cost"] + medium["total_cost"] + complex_q["total_cost"]

# Compare to using Claude Sonnet for everything
all_sonnet = estimate_cost("claude-sonnet-4", **scenario_params)

savings = all_sonnet["total_cost"] - blended_cost
savings_pct = (savings / all_sonnet["total_cost"]) * 100

print(f"  All Claude Sonnet:   ${all_sonnet['total_cost']:>12,.2f}/month")
print(f"  Tiered approach:     ${blended_cost:>12,.2f}/month")
print(f"  Monthly savings:     ${savings:>12,.2f} ({savings_pct:.0f}% reduction)")
print(f"  Annual savings:      ${savings * 12:>12,.2f}")