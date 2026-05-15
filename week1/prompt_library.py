# ============================================================
# REUSABLE PROMPT TEMPLATE LIBRARY
# This is how real AI teams manage prompts at scale
# ============================================================

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import anthropic
import json
import time
from dotenv import load_dotenv

# Load .env from project root so ANTHROPIC_API_KEY is set when run from week1/
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise SystemExit(
        "ANTHROPIC_API_KEY not set. Add it to a .env file in the project root or export it in your shell."
    )
client = anthropic.Anthropic(api_key=api_key)
COST_PER_1K_INPUT = 0.003
COST_PER_1K_OUTPUT = 0.015


@dataclass
class PromptResult:
    """Structured result from any prompt — consistent across all templates."""
    output: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    template_name: str
    template_version: str


class PromptTemplate:
    """
    A versioned, reusable prompt template.
    
    Why versioning matters: When you change a prompt in production,
    you need to know EXACTLY which version produced which outputs.
    This is the foundation of prompt eval workflows.
    """
    
    def __init__(
        self,
        name: str,
        version: str,
        system_prompt: str,
        user_prompt_template: str,  # Use {variable} placeholders
        model: str = "claude-sonnet-4-5",
        max_tokens: int = 500
    ):
        self.name = name
        self.version = version
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.model = model
        self.max_tokens = max_tokens
    
    def run(self, **kwargs) -> PromptResult:
        """
        Execute this template with the provided variables.
        
        Example: template.run(review="Great product!", product="iPhone")
        The {review} and {product} placeholders get filled in automatically.
        """
        # Fill in the template variables
        user_prompt = self.user_prompt_template.format(**kwargs)
        
        start_time = time.time()
        
        response = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Calculate cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens / 1000 * COST_PER_1K_INPUT) + \
               (output_tokens / 1000 * COST_PER_1K_OUTPUT)
        
        return PromptResult(
            output=response.content[0].text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            template_name=self.name,
            template_version=self.version
        )
    
    def run_batch(self, inputs: list[dict]) -> list[PromptResult]:
        """
        Run the template on multiple inputs and return all results.
        Useful for evals — test your prompt across 20+ inputs at once.
        """
        results = []
        for input_vars in inputs:
            result = self.run(**input_vars)
            results.append(result)
        return results
    
    def cost_estimate(self, avg_input_chars: int, avg_output_chars: int, volume: int) -> dict:
        """
        Estimate costs before running at scale.
        Rule of thumb: ~4 chars per token.
        
        This is PM-critical: always estimate before shipping.
        """
        # Rough token estimates (4 chars ≈ 1 token)
        system_tokens = len(self.system_prompt) / 4
        avg_user_tokens = avg_input_chars / 4
        total_input_tokens = (system_tokens + avg_user_tokens) * volume
        total_output_tokens = (avg_output_chars / 4) * volume
        
        total_cost = (total_input_tokens / 1000 * COST_PER_1K_INPUT) + \
                     (total_output_tokens / 1000 * COST_PER_1K_OUTPUT)
        
        return {
            "volume": volume,
            "estimated_total_cost_usd": round(total_cost, 4),
            "cost_per_request_usd": round(total_cost / volume, 6),
            "cost_per_1000_requests_usd": round(total_cost / volume * 1000, 4)
        }


# ============================================================
# BUILD YOUR TEMPLATE LIBRARY
# Three templates you'll reuse across portfolio projects
# ============================================================

# Template 1: Sentiment analysis with structured output
sentiment_template = PromptTemplate(
    name="product_sentiment",
    version="1.0",
    system_prompt="""You analyze product feedback for a product team.
Output ONLY valid JSON matching this exact schema:
{"sentiment": "POSITIVE|NEGATIVE|NEUTRAL", "confidence": 0-100, "themes": ["list", "of", "issues"], "priority": "HIGH|MEDIUM|LOW"}
priority = HIGH if safety/crashes/data loss, MEDIUM if UX issues, LOW if minor preferences""",
    user_prompt_template="Analyze this {product} review:\n\n{review}",
    max_tokens=150
)

# Template 2: PM-style document summarization
summary_template = PromptTemplate(
    name="pm_document_summary", 
    version="1.0",
    system_prompt="""You are a senior PM summarizing documents for executive review.
Structure every summary as:
**TL;DR** (1 sentence)
**Key Decision** (what action is needed)
**Risk** (biggest concern)
**Recommendation** (your call)

Be direct. No fluff. Executives read 50 docs a day.""",
    user_prompt_template="Summarize this document for an Apple VP:\n\n{document}",
    max_tokens=300
)

# Template 3: Feature tradeoff analysis
tradeoff_template = PromptTemplate(
    name="feature_tradeoff_analyzer",
    version="1.0", 
    system_prompt="""You are an AI PM at Apple evaluating feature proposals.
For every feature, output a structured analysis:
- User impact (1-10)
- Privacy risk (1-10, higher = more risk)  
- On-device feasibility (1-10, higher = more feasible locally)
- Build complexity (1-10, higher = more complex)
- Recommendation: SHIP / ITERATE / KILL with one-line rationale

Apple's priority order: Privacy > User impact > Feasibility > Complexity""",
    user_prompt_template="Evaluate this feature for {product}:\n\nFeature: {feature_description}\nContext: {context}",
    max_tokens=400
)


def demo_template_library():
    """Run all three templates with real inputs."""
    
    print("=" * 60)
    print("PROMPT TEMPLATE LIBRARY DEMO")
    print("=" * 60)
    
    # --- Template 1: Sentiment ---
    print("\n[1] SENTIMENT ANALYSIS")
    result = sentiment_template.run(
        product="AirPods Pro",
        review="The noise cancellation is incredible but they fall out during runs. Battery is fine."
    )
    print(f"Output: {result.output}")
    print(f"Cost: ${result.cost_usd:.6f} | Latency: {result.latency_ms:.0f}ms")
    
    # Cost at scale
    estimate = sentiment_template.cost_estimate(
        avg_input_chars=200,    # Typical review length
        avg_output_chars=100,   # JSON response
        volume=100_000          # 100K reviews/month
    )
    print(f"Cost at 100K reviews/month: ${estimate['estimated_total_cost_usd']}")
    
    # --- Template 2: Summary ---
    print("\n[2] PM DOCUMENT SUMMARY")
    result = summary_template.run(
        document="""Q4 User Research Report: Voice Features
        
        We interviewed 42 iPhone users about voice interaction preferences.
        78% said they avoid Siri in public due to privacy concerns about being overheard.
        61% would use voice features more if processing happened on-device.
        The main complaint was Siri misunderstanding context in multi-turn conversations.
        Android users switching to iPhone cited our privacy reputation as primary reason.
        Recommendation from research team: prioritize on-device processing for voice."""
    )
    print(f"Output:\n{result.output}")
    print(f"Cost: ${result.cost_usd:.6f} | Latency: {result.latency_ms:.0f}ms")
    
    # --- Template 3: Feature Tradeoff ---
    print("\n[3] FEATURE TRADEOFF ANALYSIS")
    result = tradeoff_template.run(
        product="iPhone",
        feature_description="Real-time emotion detection during FaceTime calls to suggest conversation improvements",
        context="Would use front camera + microphone to detect emotional cues and surface tips like 'your friend seems upset'"
    )
    print(f"Output:\n{result.output}")
    print(f"Cost: ${result.cost_usd:.6f} | Latency: {result.latency_ms:.0f}ms")
    
    print("\n" + "=" * 60)
    print("Total templates built: 3 | Ready for portfolio projects")


if __name__ == "__main__":
    demo_template_library()