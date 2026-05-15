# day4_prompt_engineering.py
# Week 1, Day 4: Prompt Engineering Fundamentals
# Goal: Build reusable prompt templates and measure their impact

import os
import anthropic
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root so ANTHROPIC_API_KEY is set when run from week1/
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Initialize the Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise SystemExit(
        "ANTHROPIC_API_KEY not set. Add it to a .env file in the project root or export it in your shell."
    )
client = anthropic.Anthropic(api_key=api_key)

# Sonnet pricing (as of early 2026): ~$3 per million input tokens, $15 per million output tokens
COST_PER_1K_INPUT_TOKENS = 0.003
COST_PER_1K_OUTPUT_TOKENS = 0.015

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate the dollar cost of an API call."""
    input_cost = (input_tokens / 1000) * COST_PER_1K_INPUT_TOKENS
    output_cost = (output_tokens / 1000) * COST_PER_1K_OUTPUT_TOKENS
    return input_cost + output_cost

# ============================================================
# PATTERN 1: ZERO-SHOT
# Just ask — no examples provided
# Best for: simple, well-understood tasks
# ============================================================

def zero_shot_example():
    """Ask Claude to classify a product review with no examples."""
    
    start_time = time.time()
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=100,           # Short output = lower cost
        messages=[
            {
                "role": "user",
                # Zero-shot: just the task, no examples
                "content": "Classify this product review as POSITIVE, NEGATIVE, or NEUTRAL. Reply with just the label.\n\nReview: 'The battery life is okay but the camera crashes constantly.'"
            }
        ]
    )
    
    latency = (time.time() - start_time) * 1000  # Convert to ms
    cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)
    
    print("=== ZERO-SHOT ===")
    print(f"Output: {response.content[0].text}")
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    print(f"Cost: ${cost:.6f}")
    print(f"Latency: {latency:.0f}ms\n")
    
    return response.content[0].text, cost, latency


# ============================================================
# PATTERN 2: FEW-SHOT
# Provide 2-3 examples before your real request
# Best for: consistent formatting, nuanced classification
# ============================================================

def few_shot_example():
    """Same task, but with examples. Notice the consistency improvement."""
    
    # The key: your examples define the exact behavior you want
    few_shot_prompt = """Classify product reviews. Reply with ONLY the label and a confidence score 0-100.
Format: LABEL (confidence)

Examples:
Review: "Best phone I've ever owned, amazing camera" → POSITIVE (95)
Review: "Stopped working after 2 days, terrible support" → NEGATIVE (98)  
Review: "It's fine, does what it says" → NEUTRAL (72)

Now classify:
Review: "The battery life is okay but the camera crashes constantly." →"""
    
    start_time = time.time()
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=20,            # We know exactly what format we want
        messages=[
            {"role": "user", "content": few_shot_prompt}
        ]
    )
    
    latency = (time.time() - start_time) * 1000
    cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)
    
    print("=== FEW-SHOT ===")
    print(f"Output: {response.content[0].text}")
    print(f"Input tokens: {response.usage.input_tokens}")  # Notice: more input tokens than zero-shot
    print(f"Output tokens: {response.usage.output_tokens}")
    print(f"Cost: ${cost:.6f}")
    print(f"Latency: {latency:.0f}ms\n")
    
    return response.content[0].text, cost, latency


# ============================================================
# PATTERN 3: CHAIN-OF-THOUGHT
# Ask the model to reason before answering
# Best for: complex decisions, reducing errors on hard tasks
# ============================================================

def chain_of_thought_example():
    """Same review, but ask Claude to reason through it first."""
    
    start_time = time.time()
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,           # More tokens needed for reasoning
        messages=[
            {
                "role": "user",
                "content": """Classify this product review as POSITIVE, NEGATIVE, or NEUTRAL.

Think through it step by step:
1. What aspects does the reviewer mention?
2. Are they positive or negative?
3. What's the overall sentiment?
Then give your final classification.

Review: "The battery life is okay but the camera crashes constantly." """
            }
        ]
    )
    
    latency = (time.time() - start_time) * 1000
    cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)
    
    print("=== CHAIN-OF-THOUGHT ===")
    print(f"Output:\n{response.content[0].text}")
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")  # Notice: much higher — you're paying for reasoning
    print(f"Cost: ${cost:.6f}")
    print(f"Latency: {latency:.0f}ms\n")
    
    return response.content[0].text, cost, latency


# ============================================================
# PATTERN 4: SYSTEM + USER SEPARATION
# System prompt = contract/persona/rules
# User prompt = the actual request
# Best for: production systems, consistent behavior across many requests
# ============================================================

def system_user_separation_example():
    """Separate concerns: system handles persona, user handles input."""
    
    start_time = time.time()
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=50,
        system="""You are a product sentiment analyzer for an Apple retail team.
Rules:
- Output ONLY valid JSON: {"label": "POSITIVE|NEGATIVE|NEUTRAL", "confidence": 0-100, "key_issue": "string"}
- key_issue: the single most important thing the reviewer mentions
- Never explain or add commentary""",
        messages=[
            {
                "role": "user",
                # Notice: user prompt is now just the raw data — clean and simple
                "content": "The battery life is okay but the camera crashes constantly."
            }
        ]
    )
    
    latency = (time.time() - start_time) * 1000
    cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)
    
    # Guard against empty or unexpected response content
    raw_text = ""
    if response.content and len(response.content) > 0 and hasattr(response.content[0], "text"):
        raw_text = response.content[0].text.strip()
    
    # Try to parse the JSON — this is what production code does
    print("=== SYSTEM + USER SEPARATION ===")
    if not raw_text:
        print("(No text in response — check API response or rate limits)")
    else:
        try:
            result = json.loads(raw_text)
            print(f"Parsed JSON: {json.dumps(result, indent=2)}")
        except json.JSONDecodeError:
            print(f"Raw output (not valid JSON): {raw_text}")
    
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    print(f"Cost: ${cost:.6f}")
    print(f"Latency: {latency:.0f}ms\n")
    
    return raw_text or "(no output)", cost, latency


def _summary_result(text: str, max_len: int = 30) -> str:
    """Truncate result for summary table; one line."""
    if not text or text == "(no output)":
        return text or "(no output)"
    one_line = text.replace("\n", " ").strip()
    return (one_line[: max_len] + "…") if len(one_line) > max_len else one_line


# Run all four patterns
if __name__ == "__main__":
    print("Running all 4 prompt patterns on the same input...\n")
    
    result1, cost1, lat1 = zero_shot_example()
    result2, cost2, lat2 = few_shot_example()
    result3, cost3, lat3 = chain_of_thought_example()
    result4, cost4, lat4 = system_user_separation_example()
    
    print("=== COMPARISON SUMMARY ===")
    print(f"{'Pattern':<25} {'Result':<32} {'Cost':>10} {'Latency':>12}")
    print("-" * 82)
    print(f"{'Zero-shot':<25} {_summary_result(result1):<32} ${cost1:<9.6f} {lat1:>8.0f}ms")
    print(f"{'Few-shot':<25} {_summary_result(result2):<32} ${cost2:<9.6f} {lat2:>8.0f}ms")
    print(f"{'Chain-of-thought':<25} {_summary_result(result3):<32} ${cost3:<9.6f} {lat3:>8.0f}ms")
    print(f"{'System+User':<25} {_summary_result(result4):<32} ${cost4:<9.6f} {lat4:>8.0f}ms")