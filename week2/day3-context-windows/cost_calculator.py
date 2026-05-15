import tiktoken

# tiktoken is a fast tokenizer — lets us count tokens BEFORE sending to the API
# Critical for cost estimation and context window management

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """
    Count tokens in a string.
    cl100k_base is the encoding used by GPT-4 and Claude models.
    Returns an integer token count.
    """
    encoder = tiktoken.get_encoding(model)
    tokens = encoder.encode(text)
    return len(tokens)

def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "claude-sonnet"
) -> dict:
    """
    Estimate API cost for a single call.
    Prices as of early 2026 — always verify current pricing.
    Returns a dict with cost breakdown.
    """
    # Pricing per million tokens (input/output often differ)
    pricing = {
        "claude-sonnet": {"input": 3.00, "output": 15.00},
        "gpt-4o":         {"input": 2.50, "output": 10.00},
        "claude-haiku":   {"input": 0.25, "output": 1.25},  # Cheaper, faster, less capable
    }
    
    rates = pricing.get(model, pricing["claude-sonnet"])
    
    input_cost  = (input_tokens  / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    
    return {
        "input_tokens":  input_tokens,
        "output_tokens": output_tokens,
        "input_cost":    round(input_cost,  6),
        "output_cost":   round(output_cost, 6),
        "total_cost":    round(input_cost + output_cost, 6),
    }

def cost_at_scale(cost_per_call: float, daily_users: int, calls_per_user: int) -> dict:
    """
    Project costs at product scale.
    This is the number that gets you taken seriously in PM interviews.
    """
    daily_cost   = cost_per_call * daily_users * calls_per_user
    monthly_cost = daily_cost * 30
    annual_cost  = daily_cost * 365
    
    return {
        "per_call":    f"${cost_per_call:.4f}",
        "daily":       f"${daily_cost:,.2f}",
        "monthly":     f"${monthly_cost:,.2f}",
        "annual":      f"${annual_cost:,.2f}",
    }

# --- Run it ---
if __name__ == "__main__":
    # Example: A customer support chat after 20 turns
    short_message  = "What time does the store close?"
    long_history   = """
    User: I bought an iPhone last week and the battery drains really fast.
    Assistant: I'm sorry to hear that. Battery drain can have several causes...
    User: I already tried turning off background refresh.
    Assistant: Good step. Let's try resetting your network settings...
    """ * 10  # Simulate 20-turn conversation by repeating 10x
    
    short_tokens  = count_tokens(short_message)
    history_tokens = count_tokens(long_history)
    total_tokens  = short_tokens + history_tokens
    
    print(f"Short message:  {short_tokens} tokens")
    print(f"Conversation history: {history_tokens} tokens")
    print(f"Total input:    {total_tokens} tokens")
    
    # Estimate cost for this single API call
    cost = estimate_cost(
        input_tokens  = total_tokens,
        output_tokens = 200,            # Typical response length
        model         = "claude-sonnet"
    )
    print(f"\nSingle call cost: ${cost['total_cost']:.4f}")
    
    # Now project to Apple scale
    # Siri handles ~500M requests/day; let's model a smaller AI feature
    scale = cost_at_scale(
        cost_per_call = cost["total_cost"],
        daily_users   = 1_000_000,   # 1M DAU — modest Apple feature
        calls_per_user = 5           # 5 AI interactions/day
    )
    print(f"\n--- Cost at 1M DAU, 5 calls/day ---")
    for k, v in scale.items():
        print(f"  {k:12}: {v}")