# model_basics.py
# Purpose: Verify connectivity to all three major LLM APIs
# and retrieve a simple response from each.
# This is your "ping test" before building the benchmarker.

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import anthropic
import openai
import time
import os

# ── Helper: call Claude ──────────────────────────────────────────────────────

def call_claude(prompt: str) -> dict:
    """
    Sends a prompt to Claude and returns response + metadata.
    Returns a dict so we can compare apples-to-apples across models.
    """
    client = anthropic.Anthropic()  # Picks up ANTHROPIC_API_KEY from environment
    
    start = time.time()  # Start timing BEFORE the API call
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    
    elapsed = (time.time() - start) * 1000  # Convert to milliseconds
    
    return {
        "model": "claude-sonnet-4",
        "response": message.content[0].text,
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "latency_ms": round(elapsed, 1)
    }

# ── Helper: call GPT-4o ──────────────────────────────────────────────────────

def call_gpt4(prompt: str) -> dict:
    """
    Sends a prompt to GPT-4o and returns response + metadata.
    Note: OpenAI's SDK structure differs slightly from Anthropic's.
    """
    client = openai.OpenAI()  # Picks up OPENAI_API_KEY from environment
    
    start = time.time()
    
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    
    elapsed = (time.time() - start) * 1000
    
    return {
        "model": "gpt-4o",
        "response": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "latency_ms": round(elapsed, 1)
    }

# ── Run a quick test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_prompt = "In one sentence: what is a transformer neural network?"
    
    print("Testing Claude...")
    claude_result = call_claude(test_prompt)
    print(f"  Response: {claude_result['response']}")
    print(f"  Latency: {claude_result['latency_ms']}ms")
    print(f"  Tokens: {claude_result['input_tokens']} in / {claude_result['output_tokens']} out\n")
    
    print("Testing GPT-4o...")
    gpt_result = call_gpt4(test_prompt)
    print(f"  Response: {gpt_result['response']}")
    print(f"  Latency: {gpt_result['latency_ms']}ms")
    print(f"  Tokens: {gpt_result['input_tokens']} in / {gpt_result['output_tokens']} out\n")
    
    print("✅ Both APIs responding. Ready for benchmarking.")