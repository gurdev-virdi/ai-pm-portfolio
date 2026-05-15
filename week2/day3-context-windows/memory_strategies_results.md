=================================================================
MEMORY STRATEGY COMPARISON
=================================================================

--- Turn 1: 'Hi! I'm planning a trip to Japan in April....' ---

  [Full History   ] tokens=  24 | cost=$0.00013 |  3303ms
  [Sliding Window ] tokens=  24 | cost=$0.00013 |  2940ms
  [Summarization  ] tokens=  24 | cost=$0.00013 |  2904ms

--- Turn 2: 'I want to visit Tokyo and Kyoto. Which should I st...' ---
  [Full History   ] tokens= 337 | cost=$0.00021 |  4006ms
  [Sliding Window ] tokens= 306 | cost=$0.00020 |  3867ms
  [Summarization  ] tokens= 325 | cost=$0.00021 |  4340ms

--- Turn 3: 'I have about 10 days total. How should I split my ...' ---
  [Full History   ] tokens= 661 | cost=$0.00029 |  3045ms
  [Sliding Window ] tokens= 603 | cost=$0.00028 |  2802ms
  [Summarization  ] tokens= 727 | cost=$0.00031 |  3148ms

--- Turn 4: 'What's the best way to get between those cities?...' ---
  [Full History   ] tokens= 971 | cost=$0.00037 |  3825ms
  [Sliding Window ] tokens= 625 | cost=$0.00028 |  4383ms
  [Summarization  ] tokens= 725 | cost=$0.00031 |  4132ms

--- Turn 5: 'Going back to my trip — what did I say my travel m...' ---
  [Full History   ] tokens=1299 | cost=$0.00045 |  1074ms
  [Sliding Window ] tokens= 631 | cost=$0.00028 |  1417ms
  [Summarization  ] tokens= 763 | cost=$0.00032 |   962ms

=================================================================
TOTAL COST ACROSS ALL TURNS
=================================================================
  Full History        : $0.0014 total |  3292 tokens | 3051ms avg latency
  Sliding Window      : $0.0012 total |  2189 tokens | 3082ms avg latency
  Summarization       : $0.0013 total |  2564 tokens | 3097ms avg latency

=================================================================
MEMORY RECALL TEST (Turn 5 — 'What month did I say?')
=================================================================
  Full History        : ✅ Recalled April
    Response: You said you're planning a trip in **April**!

That's why I've been mentioning cherry blossoms, the ...
  Sliding Window      : ❌ Forgot
    Response: You didn't mention a specific travel month in our conversation! We've been discussing a 10-day Tokyo...
  Summarization       : ✅ Recalled April
    Response: You said you're traveling in **April**.

April is ideal for Japan—cherry blossom season (sakura) is ...