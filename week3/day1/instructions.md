# Confirm Python and key libraries
python3 --version          # Should be 3.11+
pip show anthropic openai  # Should show installed versions
pip show pytest            # If missing: pip install pytest

# Create today's working directory
mkdir -p ~/ai-pm-learning/week3/day1
cd ~/ai-pm-learning/week3/day1
touch evals_intro.py test_cases.json
```

No new installs today — this lesson is concept-heavy by design. The hands-on build starts Day 2.

---

## **10–40 min | Core Learning: The Eval Mindset**

### **Why evals exist**

Traditional software has deterministic outputs. Given input X, you get output Y — always. You test it once, it passes, you ship.

AI doesn't work that way. Given input X, you get output Y... usually. Sometimes Y'. Occasionally something completely wrong. The model is a probability distribution, not a function. **Evals are how you bring engineering discipline to probabilistic systems.**

This is why Anthropic treats eval quality as existential. You can't know if Claude is getting better or worse at a task without a rigorous eval suite. Every model update, every prompt change, every new feature — the eval suite tells you if you helped or hurt.

### **The three types of evals**

**1. Deterministic / Rule-Based**
The output must contain or match something specific. Fast, cheap, no ambiguity.
```
Input:  "Summarize this in 3 bullet points"
Assert: output.count("•") == 3  OR  len(output.split("\n")) >= 3
```

Best for: format compliance, factual assertions, safety filters ("does this output contain PII?")

**2. Model-Graded**
You use a second LLM call to judge the first output. Slower and costs tokens, but scales to subjective quality.
```
Evaluator prompt: "Rate this summary 1-5 for accuracy vs the source document.
                   Source: [original]
                   Summary: [model output]
                   Return only the integer score."

Best for: quality judgments, tone, helpfulness, relevance — things humans care about but are hard to rule-check

**3. Human Evaluation
A person reviews outputs and scores them. Gold standard, but doesn't scale.

Best for: calibrating your model-graded evals, high-stakes edge cases, final acceptance criteria before launch
The PM mental model: evals are acceptance criteria
Here's the reframe that makes this click for experienced PMs:

Writing evals is the same skill as writing acceptance criteria — applied to AI outputs instead of feature behavior.

You already know how to write "Given [state], when [action], then [outcome]." Evals are that exact structure, run automatically at scale.
Traditional ACEval Equivalent"User can submit form with valid email""Given email prompt, output contains @ symbol""Error message appears on invalid input""Given adversarial input, output does NOT contain harmful content""Search returns relevant results""Given query, model-graded relevance score ≥ 4/5"
What makes a good eval suite
A strong eval suite has:

Coverage — happy path, edge cases, adversarial inputs
Balance — mix of deterministic (fast) and model-graded (nuanced)
Baselines — a score before any changes, so you can measure delta
Failure modes — tests specifically designed to catch known bad behaviors

At Anthropic, the eval suite isn't a QA afterthought — it's written before the feature, just like good acceptance criteria. This will come up in your interview.