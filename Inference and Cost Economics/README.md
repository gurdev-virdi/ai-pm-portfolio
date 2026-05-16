# Week 1: Local vs cloud inference & cost calculator

## Cost calculator — how it’s built

The cost calculator in `cloud_apis.py` is built to support **production-scale projections** and **model choice decisions** using **cost** and **latency** (quality is planned for a future version).

### Production-scale projections

- **Per-call cost** is computed from real API responses: `calculate_cost(input_tokens, output_tokens, model)` uses the `PRICING` table ($ per million tokens, in/out) so each call gets a dollar cost.
- **Scale scenarios** (10K, 100K, 1M, 10M calls/day) multiply that per-call cost by volume. You see daily cost per model at each scale.
- **Annualized view** (e.g. 10M calls/day × 365) is framed as a “headcount decision” so the cost difference between models is interpretable for product and eng planning.

So the calculator doesn’t assume a fixed volume; it takes a **representative prompt**, measures tokens and latency once, then projects cost at any volume you care about.

### Model choice: cost and latency

- **Cost:** The comparison report shows cost per call and cost per 1M calls for each model. The “KEY INSIGHT” section states which model is cheaper, by what percentage, and the daily/yearly dollar gap at 10M calls/day. That supports choosing a model when budget is the main constraint.
- **Latency:** Every API call is timed; the report table includes latency (ms) per model. So you can weigh “cheaper but slower” vs “faster but more expensive” for your product’s latency requirements.

Together, cost and latency let you think through tradeoffs (e.g. “Use Haiku for high-volume, low-latency paths; use Sonnet only where we need higher quality”) before committing to a model mix.

### Future: quality in the calculator

Today the calculator does **not** include quality (e.g. correctness, relevance, or user satisfaction). A future version will add quality metrics so model choice can be decided along three axes: **cost**, **latency**, and **quality**.
