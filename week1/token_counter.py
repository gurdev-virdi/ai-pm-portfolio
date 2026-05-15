import tiktoken
import anthropic
import json
from dataclasses import dataclass

@dataclass
class TokenCost:
    model: str
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float

# Pricing per 1M tokens (base input/output). Last verified Feb 2025.
# Sources: docs.anthropic.com/en/docs/about-claude/pricing, platform.openai.com/docs/pricing
PRICING = {
    "claude-haiku-3": {"input": 0.25, "output": 1.25},
    "claude-haiku-3.5": {"input": 0.80, "output": 4.00},
    "claude-haiku-4.5": {"input": 1.00, "output": 5.00},
    "claude-sonnet-3-5": {"input": 3.00, "output": 15.00},  # same as Sonnet 4.x
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}

def count_tokens_openai(text: str, model: str = "gpt-4o") -> int:
    """Count tokens using tiktoken (works for OpenAI models)."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def estimate_cost(model: str, input_text: str, output_text: str) -> TokenCost:
    """Calculate exact cost for a single API call."""
    if model not in PRICING:
        raise ValueError(f"Unknown model: {model}. Add to PRICING dict.")
    
    pricing = PRICING[model]
    
    # Use tiktoken for estimation (Claude uses similar tokenization)
    enc = tiktoken.get_encoding("cl100k_base")
    input_tokens = len(enc.encode(input_text))
    output_tokens = len(enc.encode(output_text))
    
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    
    return TokenCost(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost_usd=round(input_cost, 6),
        output_cost_usd=round(output_cost, 6),
        total_cost_usd=round(input_cost + output_cost, 6)
    )

def scale_cost(single_cost: TokenCost, daily_users: int, calls_per_user: int) -> dict:
    """Project costs at scale — the PM question every interviewer asks."""
    daily_calls = daily_users * calls_per_user
    monthly_calls = daily_calls * 30
    
    return {
        "daily_cost_usd": round(single_cost.total_cost_usd * daily_calls, 2),
        "monthly_cost_usd": round(single_cost.total_cost_usd * monthly_calls, 2),
        "annual_cost_usd": round(single_cost.total_cost_usd * monthly_calls * 12, 2),
        "cost_per_user_per_month": round(single_cost.total_cost_usd * calls_per_user * 30, 4)
    }

if __name__ == "__main__":
    # Test with a realistic prompt
    sample_prompt = """You are a helpful assistant. The user has asked: 
    Summarize this document and extract the 3 key action items."""
    
    sample_output = """Here are the 3 key action items from the document:
    1. Schedule follow-up meeting by Friday
    2. Complete technical review of proposal  
    3. Send updated budget to stakeholders"""
    
    cost = estimate_cost("claude-haiku-3", sample_prompt, sample_output)
    print(f"\n📊 Single call cost breakdown:")
    print(f"  Model: {cost.model}")
    print(f"  Input: {cost.input_tokens} tokens = ${cost.input_cost_usd}")
    print(f"  Output: {cost.output_tokens} tokens = ${cost.output_cost_usd}")
    print(f"  Total: ${cost.total_cost_usd}")
    
    scale = scale_cost(cost, daily_users=100_000, calls_per_user=3)
    print(f"\n📈 At scale (100K daily users, 3 calls/user):")
    print(f"  Daily cost: ${scale['daily_cost_usd']:,}")
    print(f"  Monthly cost: ${scale['monthly_cost_usd']:,}")
    print(f"  Annual cost: ${scale['annual_cost_usd']:,}")
    print(f"  Per user/month: ${scale['cost_per_user_per_month']}")