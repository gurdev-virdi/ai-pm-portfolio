⚡ Reusable eval prompt

You are an AI PM writing an eval suite for a new AI feature.

Feature description: [PASTE YOUR FEATURE DESCRIPTION]

Generate 10 test cases covering:
- 3 happy path cases (normal expected usage)
- 2 edge cases (unusual but valid inputs)
- 2 adversarial cases (prompt injection, malformed input)
- 2 quality cases (model-graded, subjective quality checks)
- 1 performance case (latency or format constraint)

For each test case output:
- ID (TC001, TC002...)
- Description (one sentence)
- Input (the actual test input)
- Eval type (deterministic / model_graded / human)
- Assertion (what you check)
- Expected behavior (what good looks like)

Return as JSON array.
