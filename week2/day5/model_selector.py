# model_selector.py
# A decision framework that recommends a model given product requirements.
# This is PM thinking translated into code.

from dataclasses import dataclass

@dataclass
class ProductRequirements:
    """
    The inputs a PM would define for their product.
    Each field maps to a real product constraint.
    """
    max_latency_ms: int        # User-facing latency budget (100ms = on-device, 2000ms = cloud ok)
    max_cost_per_1k: float     # Cost budget per 1,000 calls in USD
    needs_privacy: bool        # True = data cannot leave device or must use Private Cloud Compute
    min_context_tokens: int    # Minimum context window needed
    task_complexity: str       # "simple" | "moderate" | "complex"
    deployment: str            # "on_device" | "private_cloud" | "cloud"


# Model registry — in production this would pull from a live config
MODEL_REGISTRY = [
    {
        "name": "Apple Intelligence (on-device)",
        "provider": "Apple",
        "approx_params": "3B",
        "latency_ms_p50": 80,       # Fast — runs on Neural Engine
        "cost_per_1k_usd": 0.00,    # No API cost; compute is local
        "privacy": "on_device",
        "context_tokens": 4096,
        "complexity_ceiling": "moderate",
        "deployment": "on_device",
        "notes": "Apple Intelligence small model. Ideal for real-time features."
    },
    {
        "name": "Apple Private Cloud Compute",
        "provider": "Apple",
        "approx_params": "~70B equiv",
        "latency_ms_p50": 600,
        "cost_per_1k_usd": 0.00,    # Internal cost absorbed by Apple infra
        "privacy": "private_cloud",  # Apple's PCC: no data retention, hardware attestation
        "context_tokens": 32000,
        "complexity_ceiling": "complex",
        "deployment": "private_cloud",
        "notes": "For complex tasks that exceed on-device capability. Privacy preserved."
    },
    {
        "name": "claude-3-5-haiku",
        "provider": "Anthropic",
        "approx_params": "~10B",
        "latency_ms_p50": 800,
        "cost_per_1k_usd": 0.0056,   # ~$0.80/1M input + $4/1M output blended
        "privacy": "cloud",
        "context_tokens": 200000,
        "complexity_ceiling": "moderate",
        "deployment": "cloud",
        "notes": "Fast, cheap Claude. Best for high-volume moderate tasks."
    },
    {
        "name": "claude-3-5-sonnet",
        "provider": "Anthropic",
        "approx_params": "~70B equiv",
        "latency_ms_p50": 1800,
        "cost_per_1k_usd": 0.063,
        "privacy": "cloud",
        "context_tokens": 200000,
        "complexity_ceiling": "complex",
        "deployment": "cloud",
        "notes": "Best reasoning quality in Claude lineup. Use when quality > cost."
    },
    {
        "name": "gpt-4o-mini",
        "provider": "OpenAI",
        "approx_params": "~8B equiv",
        "latency_ms_p50": 700,
        "cost_per_1k_usd": 0.00048,
        "privacy": "cloud",
        "context_tokens": 128000,
        "complexity_ceiling": "moderate",
        "deployment": "cloud",
        "notes": "Cheapest capable cloud model. OpenAI data retention applies."
    },
    {
        "name": "gpt-4o",
        "provider": "OpenAI",
        "approx_params": "~200B equiv",
        "latency_ms_p50": 2000,
        "cost_per_1k_usd": 0.045,
        "privacy": "cloud",
        "context_tokens": 128000,
        "complexity_ceiling": "complex",
        "deployment": "cloud",
        "notes": "High quality, multimodal. Consider for vision tasks."
    },
]

# Map complexity to a numeric score so we can filter
COMPLEXITY_RANK = {"simple": 1, "moderate": 2, "complex": 3}


def select_model(req: ProductRequirements) -> None:
    """
    Given product requirements, recommend suitable models with reasoning.
    This is the PM decision process made explicit.
    """
    candidates = []

    for model in MODEL_REGISTRY:
        reasons_pass  = []
        reasons_fail  = []

        # ── Filter 1: Latency ─────────────────────────────────────────────
        if model["latency_ms_p50"] <= req.max_latency_ms:
            reasons_pass.append(
                f"Latency {model['latency_ms_p50']}ms ≤ budget {req.max_latency_ms}ms"
            )
        else:
            reasons_fail.append(
                f"Too slow: {model['latency_ms_p50']}ms > {req.max_latency_ms}ms"
            )

        # ── Filter 2: Cost ────────────────────────────────────────────────
        if model["cost_per_1k_usd"] <= req.max_cost_per_1k:
            reasons_pass.append(
                f"Cost ${model['cost_per_1k_usd']}/1K ≤ budget ${req.max_cost_per_1k}/1K"
            )
        else:
            reasons_fail.append(
                f"Too expensive: ${model['cost_per_1k_usd']}/1K > ${req.max_cost_per_1k}/1K"
            )

        # ── Filter 3: Privacy ─────────────────────────────────────────────
        # If privacy required, must be on_device or private_cloud
        if req.needs_privacy:
            if model["privacy"] in ("on_device", "private_cloud"):
                reasons_pass.append("Privacy-safe deployment")
            else:
                reasons_fail.append("Fails privacy: data sent to external cloud")

        # ── Filter 4: Context window ──────────────────────────────────────
        if model["context_tokens"] >= req.min_context_tokens:
            reasons_pass.append(
                f"Context {model['context_tokens']} ≥ required {req.min_context_tokens}"
            )
        else:
            reasons_fail.append(
                f"Context too small: {model['context_tokens']} < {req.min_context_tokens}"
            )

        # ── Filter 5: Task complexity ─────────────────────────────────────
        model_rank = COMPLEXITY_RANK[model["complexity_ceiling"]]
        task_rank  = COMPLEXITY_RANK[req.task_complexity]

        if model_rank >= task_rank:
            reasons_pass.append(
                f"Handles '{req.task_complexity}' complexity"
            )
        else:
            reasons_fail.append(
                f"Complexity ceiling '{model['complexity_ceiling']}' < required '{req.task_complexity}'"
            )

        # ── Filter 6: Deployment match ────────────────────────────────────
        if req.deployment == "on_device" and model["deployment"] != "on_device":
            reasons_fail.append("Deployment mismatch: need on-device")
        elif req.deployment == "private_cloud" and model["deployment"] not in ("on_device", "private_cloud"):
            reasons_fail.append("Deployment mismatch: need private cloud or on-device")

        candidates.append({
            "model": model,
            "passes": len(reasons_fail) == 0,
            "pass_count": len(reasons_pass),
            "fail_count": len(reasons_fail),
            "reasons_pass": reasons_pass,
            "reasons_fail": reasons_fail,
        })

    # Sort: passing models first, then by most criteria met
    candidates.sort(key=lambda x: (x["passes"], x["pass_count"]), reverse=True)

    # ── Print recommendation ──────────────────────────────────────────────────
    print("\n" + "="*65)
    print("MODEL SELECTION RECOMMENDATION")
    print("="*65)
    print(f"Requirements: latency≤{req.max_latency_ms}ms | "
          f"cost≤${req.max_cost_per_1k}/1K | "
          f"privacy={req.needs_privacy} | "
          f"complexity={req.task_complexity}")
    print()

    passing = [c for c in candidates if c["passes"]]
    failing = [c for c in candidates if not c["passes"]]

    if passing:
        print("✅ RECOMMENDED MODELS:")
        for c in passing:
            m = c["model"]
            print(f"\n  {m['name']} ({m['provider']})")
            print(f"  {m['notes']}")
            for r in c["reasons_pass"]:
                print(f"    ✓ {r}")
    else:
        print("⚠️  No model meets ALL requirements. Closest options:")
        for c in failing[:2]:
            m = c["model"]
            print(f"\n  {m['name']} — passes {c['pass_count']}/{c['pass_count']+c['fail_count']} criteria")
            for r in c["reasons_fail"]:
                print(f"    ✗ {r}")

    print("\n" + "="*65)


# ── Test three realistic Apple product scenarios ──────────────────────────────
if __name__ == "__main__":

    print("\n📱 SCENARIO 1: Siri on-device quick reply suggestions")
    select_model(ProductRequirements(
        max_latency_ms=150,          # Must feel instant
        max_cost_per_1k=0.00,        # Can't charge per Siri call
        needs_privacy=True,          # Apple's core promise
        min_context_tokens=2048,
        task_complexity="simple",
        deployment="on_device"
    ))

    print("\n📄 SCENARIO 2: Apple Intelligence writing tools (longer docs)")
    select_model(ProductRequirements(
        max_latency_ms=2000,         # User is actively waiting; 2s ok
        max_cost_per_1k=0.10,        # Internal infra cost ok
        needs_privacy=True,          # Documents are sensitive
        min_context_tokens=16000,    # Need to process full documents
        task_complexity="complex",
        deployment="private_cloud"
    ))

    print("\n🔍 SCENARIO 3: Third-party app using Apple AI APIs (developer tool)")
    select_model(ProductRequirements(
        max_latency_ms=3000,
        max_cost_per_1k=0.05,
        needs_privacy=False,         # Developer chose to use cloud
        min_context_tokens=8000,
        task_complexity="moderate",
        deployment="cloud"
    ))