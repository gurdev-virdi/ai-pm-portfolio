## Results of running day4_prompt_engineering.py on Feb 18, 2026

=== ZERO-SHOT ===
Output: NEGATIVE
Input tokens: 45
Output tokens: 5
Cost: $0.000210
Latency: 1426ms

=== FEW-SHOT ===
Output: NEGATIVE (82)
Input tokens: 120
Output tokens: 8
Cost: $0.000480
Latency: 1321ms

=== CHAIN-OF-THOUGHT ===
Output:
Let me work through this step by step:

## 1. What aspects does the reviewer mention?

- **Battery life** - described as "okay"
- **Camera functionality** - described as "crashes constantly"

## 2. Are they positive or negative?

- **Battery life ("okay")**: This is a neutral/lukewarm comment - not particularly praise, but not a complaint either
- **Camera crashes constantly**: This is clearly negative - "constantly" indicates a persistent, serious problem that would significantly impact user experience

## 3. What's the overall sentiment?

The review contains one neutral aspect and one strongly negative aspect. The camera crashing constantly is a significant functional problem that would make the product frustrating to use. The negative issue outweighs the neutral comment about battery life.

## Final Classification: **NEGATIVE**

The persistent camera crashing represents a major defect that dominates the review's sentiment, making this overall a negative review despite the neutral mention of battery life.
Input tokens: 82
Output tokens: 215
Cost: $0.003471
Latency: 5822ms

Raw output (not valid JSON): ```json
{
  "label": "NEGATIVE",
  "confidence": 85,
  "key_issue": "camera crashes constantly"
}
```
Input tokens: 91
Output tokens: 40
Cost: $0.000873
Latency: 1587ms

=== COMPARISON SUMMARY ===
Pattern                         Cost      Latency
--------------------------------------------------
Zero-shot                 $0.000210      1426ms
Few-shot                  $0.000480      1321ms
Chain-of-thought          $0.003471      5822ms
System+User               $0.000873      1587ms