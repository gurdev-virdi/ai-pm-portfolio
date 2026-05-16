# AI Product Management Portfolio

A hands-on, code-forward curriculum for PMs building or shipping AI products. Each week combines executable Python, real benchmark results, and PM decision frameworks — so the concepts connect directly to the tradeoffs you'll face in the job.

---

## What You'll Learn

### Week 1 — Inference & Cost Economics
- On-device vs cloud inference: latency, privacy, and capability tradeoffs
- Token economics: how models price input/output and what that means at scale
- Tiered routing: routing requests by complexity to minimize cost without sacrificing quality
- Prompt engineering patterns and a reusable prompt library

### Week 2 — RAG, Context Windows & Model Selection
- Embeddings and semantic similarity from first principles
- Chunking strategies and their impact on retrieval quality
- Building a complete RAG pipeline in ~80 lines of Python
- Retrieval evaluation: hit rate, MRR, and building test query sets
- Context window cost projections for long-conversation products
- Constraint-based model selection: matching model to task by latency, cost, and complexity

### Week 3 — Evaluation Frameworks
- Eval mindset: treating AI output like an acceptance test, not a vibe check
- Three eval types: deterministic (rule-based), model-graded, and human
- Anatomy of a rigorous eval suite: happy path, edge cases, adversarial inputs
- Building and running an eval harness; generating eval reports

---

## Project Structure

```
ai-pm-portfolio/
├── week1/                          # Inference tradeoffs & token economics
│   ├── cloud_apis.py               # Multi-provider API calls + cost calculator
│   ├── local_inference.py          # On-device inference via Ollama
│   ├── token_counter.py            # Tokenization breakdowns across languages
│   ├── token_economics.md          # Pricing table + tiered routing analysis
│   └── prompt_library.py           # Reusable prompt patterns for PM tasks
│
├── week2/
│   ├── day1/                       # Embeddings & chunking
│   │   ├── embeddings_demo.py      # Semantic similarity from scratch
│   │   ├── chunking_compare.py     # Fixed vs recursive chunk strategies
│   │   └── mini_rag.py             # Complete RAG pipeline (~80 lines)
│   ├── day2/                       # Retrieval evaluation
│   │   └── retreival_eval.py       # Hit rate + MRR across test queries
│   ├── day3-context-windows/       # Long-context cost & memory strategies
│   │   ├── memory_strategies.py    # Summarization, sliding window, hierarchical
│   │   └── cost_calculator.py      # Monthly/annual cost projections at scale
│   ├── day4/                       # Model benchmarking
│   │   ├── benchmark_harness.py    # Runs 4 eval dimensions across 2 models
│   │   └── benchmark_result.md     # Claude Sonnet 4 vs GPT-4o results
│   └── day5/                       # Model selection
│       ├── model_selector.py       # Constraint-based model picker
│       └── model_comparison.py     # Cost/latency tradeoff analysis
│
├── week3/
│   ├── day1/                       # Eval theory & test case design
│   │   ├── evals_intro.py          # Eval concepts and types
│   │   └── test_cases.json         # Example eval suite (PRD summarizer)
│   └── day2/                       # Running and reporting evals
│       ├── eval_runner.py          # Eval execution framework
│       └── eval_report.py          # Results reporting
│
├── day4-prompt-engineering/        # Prompt engineering exercises & setup
├── practice_questions/             # PM interview scenarios with worked answers
├── prompt_library/                 # Reusable prompts (eval suite generator, etc.)
├── requirements.txt
└── test_setup.py                   # Verify API keys are configured
```

---

## Key Results

### Tiered model routing cuts costs 79%

For a smart reply feature at 1M users sending 5 replies/day, routing by complexity rather than using Claude Sonnet for everything:

| Strategy | Monthly Cost |
|---|---|
| All Claude Sonnet 4 | $562,500 |
| Tiered (Gemini Flash / GPT-4o / Sonnet) | $116,100 |
| **Savings** | **$446,400 (79%) → $5.4M/year** |

### Chunking strategy changes retrieval quality

On a multi-fact query ("How much does PhotoSync Pro cost for students?"):

| Strategy | Result |
|---|---|
| Fixed chunks (300 chars) | Split facts across boundaries — partial answers only |
| Recursive chunks (400 chars, 50% overlap) | Still partial |
| Large recursive chunks (800 chars) | Retrieved both facts in a single chunk |

### Claude Sonnet 4 vs GPT-4o benchmark

Tested across instruction following, context fidelity, structured output, and conciseness:

| Metric | Claude Sonnet 4 | GPT-4o |
|---|---|---|
| Avg latency | 2,643ms | 1,374ms |
| Avg cost/call | $0.00103 | $0.00043 |
| Format compliance | Pass | Pass |
| Structured JSON | Pass | Pass |

GPT-4o is ~2x faster and ~2.4x cheaper per call. Claude Sonnet 4 produces more complete responses. The right choice depends on your latency budget and quality bar.

---

## Setup

**Prerequisites:** Python 3.10+, an Anthropic API key, an OpenAI API key. For local inference: Ollama installed with a model pulled (e.g. `ollama pull llama3.2`).

```bash
# Install dependencies
pip install -r requirements.txt

# Add API keys
cp .env.example .env
# Edit .env and fill in ANTHROPIC_API_KEY and OPENAI_API_KEY

# Verify setup
python test_setup.py
```

For local inference setup, see [`day4-prompt-engineering/instructions.md`](day4-prompt-engineering/instructions.md).

---

## How to Navigate

Work through the weeks sequentially — each builds on the prior one. Within each week, the numbered days follow a progression from concept to implementation to evaluation.

- **Interview prep:** `practice_questions/` has PM decision scenarios with worked trade-off analyses
- **Reusable prompts:** `prompt_library/` includes an eval suite generator you can drop into any feature
- **Quick reference:** each week's `.md` files contain the actual benchmark output so you can read results without re-running code

---

## Tech Stack

| Category | Tools |
|---|---|
| LLM providers | Anthropic Claude, OpenAI GPT |
| Embeddings & vector DB | ChromaDB, LangChain |
| Orchestration | LangGraph |
| Data & analytics | Pandas, NumPy |
| Visualization | Altair, Streamlit |
| Testing | pytest, LangSmith |
