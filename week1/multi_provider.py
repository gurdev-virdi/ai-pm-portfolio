import os
import time
from dotenv import load_dotenv
import anthropic
import openai
from token_counter import estimate_cost

load_dotenv()

client_anthropic = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
client_openai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_claude(prompt: str, model: str = "claude-haiku-4-5") -> dict:
    """Call Claude and return response with timing."""
    start = time.time()
    
    message = client_anthropic.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    latency_ms = round((time.time() - start) * 1000)
    output = message.content[0].text
    cost = estimate_cost("claude-haiku-4.5", prompt, output)
    
    return {
        "provider": "Anthropic Claude Haiku 4.5",
        "output": output,
        "latency_ms": latency_ms,
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
        "cost_usd": cost.total_cost_usd
    }

def call_gpt(prompt: str, model: str = "gpt-4o-mini") -> dict:
    """Call GPT and return response with timing."""
    start = time.time()
    
    response = client_openai.chat.completions.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    latency_ms = round((time.time() - start) * 1000)
    output = response.choices[0].message.content
    cost = estimate_cost("gpt-4o-mini", prompt, output)
    
    return {
        "provider": "OpenAI GPT-4o-mini",
        "output": output,
        "latency_ms": latency_ms,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "cost_usd": cost.total_cost_usd
    }

def compare_providers(prompt: str) -> None:
    """Run the same prompt through both providers and compare."""
    print(f"\n{'='*60}")
    print(f"PROMPT: {prompt[:100]}...")
    print(f"{'='*60}\n")
    
    results = []
    
    for call_fn in [call_claude, call_gpt]:
        try:
            result = call_fn(prompt)
            results.append(result)
            print(f"▶ {result['provider']}")
            print(f"  Latency: {result['latency_ms']}ms")
            print(f"  Tokens: {result['input_tokens']} in / {result['output_tokens']} out")
            print(f"  Cost: ${result['cost_usd']}")
            print(f"  Output:\n  {result['output'][:300]}\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    if len(results) == 2:
        faster = min(results, key=lambda x: x['latency_ms'])
        cheaper = min(results, key=lambda x: x['cost_usd'])
        print(f"📊 Winner on speed: {faster['provider']} ({faster['latency_ms']}ms)")
        print(f"💰 Winner on cost: {cheaper['provider']} (${cheaper['cost_usd']})")

if __name__ == "__main__":
    test_prompt = """Analyze this product decision: 
    Apple is considering adding an on-device AI writing assistant to iOS. 
    The model must run locally (no server calls). 
    List the top 3 technical constraints and top 3 user benefits, briefly."""
    
    compare_providers(test_prompt)