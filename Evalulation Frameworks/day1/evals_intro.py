import json
from pathlib import Path

_DIR = Path(__file__).resolve().parent
with open(_DIR / "test_cases.json") as f:
    test_cases = json.load(f)

print(f"\n=== EVAL SUITE SUMMARY ===")
print(f"Total test cases: {len(test_cases)}")

deterministic = [tc for tc in test_cases if tc["eval_type"] == "deterministic"]
model_graded = [tc for tc in test_cases if tc["eval_type"] == "model_graded"]
human = [tc for tc in test_cases if tc["eval_type"] == "human"]

print(f"Deterministic: {len(deterministic)}")
print(f"Model-graded:  {len(model_graded)}")
print(f"Human:         {len(human)}")

print(f"\nTest cases loaded:")
for tc in test_cases:
    print(f"  [{tc['eval_type'].upper()[:4]}] {tc['id']}: {tc['description']}")

print(f"\n✅ Eval suite initialized. Ready for Day 2 automation.")