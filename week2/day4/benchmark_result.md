
============================================================
AI MODEL BENCHMARK HARNESS
Running 4 tests × 2 models = 8 API calls
============================================================


📋 Test: Instruction Following
   Eval hint: Check: exactly 3 items, numbered format, no extra text
--------------------------------------------------

  🤖 Claude Sonnet 4:
  Response: 1. Enhanced privacy and data security by keeping sensitive information locally on the device
2. Reduced latency and faster response times by eliminating the need for cloud connectivity
3. Lower operat...
  Latency: 3605.8ms | Tokens: 52in/53out | Cost: $0.000951
  Auto-scores: {'format_correct': True, 'no_extra_text': True}

  🤖 GPT-4o:
  Response: 1. Privacy preservation
2. Reduced latency
3. Offline functionality
  Latency: 1651.3ms | Tokens: 49in/14out | Cost: $0.000262
  Auto-scores: {'format_correct': True, 'no_extra_text': True}

📋 Test: Context Fidelity (RAG simulation)
   Eval hint: Check: answer grounded in context, no hallucinated additions
--------------------------------------------------

  🤖 Claude Sonnet 4:
  Response: Based on the provided context, Apple's primary reason for on-device processing is to ensure that personal information never leaves the user's device, which prevents Apple's servers from seeing raw dat...
  Latency: 1912.9ms | Tokens: 100in/60out | Cost: $0.001200

  🤖 GPT-4o:
  Response: Apple's primary reason for on-device processing is to ensure that personal information never leaves the user's device.
  Latency: 1366.4ms | Tokens: 87in/20out | Cost: $0.000418

📋 Test: Structured Output (JSON)
   Eval hint: Check: valid JSON, all 3 fields present, correct data types
--------------------------------------------------

  🤖 Claude Sonnet 4:
  Response: {"model_name": "Claude 3.5 Sonnet", "best_use_case": "Complex reasoning, analysis, and creative writing tasks requiring nuanced understanding", "latency_tier": "medium"}
  Latency: 1909.0ms | Tokens: 70in/50out | Cost: $0.000960
  Auto-scores: {'valid_json': True, 'has_all_fields': True}

  🤖 GPT-4o:
  Response: {
    "model_name": "AssistantGPT",
    "best_use_case": "Customer Support",
    "latency_tier": "medium"
}
  Latency: 784.3ms | Tokens: 71in/31out | Cost: $0.000487
  Auto-scores: {'valid_json': True, 'has_all_fields': True}

📋 Test: Conciseness Under Constraint
   Eval hint: Check: word count ≤50, substantive content included
--------------------------------------------------

  🤖 Claude Sonnet 4:
  Response: Apple Intelligence is Apple's AI system that runs locally on devices using specialized chips. It processes personal data privately on-device for features like writing assistance, photo search, and Sir...
  Latency: 3143.4ms | Tokens: 20in/62out | Cost: $0.000990
  Auto-scores: {'word_count': 47, 'within_limit': True}

  🤖 GPT-4o:
  Response: Apple Intelligence combines machine learning, data analysis, and on-device processing to enhance user experience. It powers features like predictive text, Siri, image recognition, and personalized app...
  Latency: 1692.0ms | Tokens: 18in/52out | Cost: $0.000565
  Auto-scores: {'word_count': 44, 'within_limit': True}


============================================================
BENCHMARK SUMMARY
============================================================
╭───────────────────────────┬─────────────────┬───────────────┬─────────────┬──────────────┬───────────┬─────────────────────────────────────────────────╮
│ Test                      │ Model           │   Latency(ms) │   In Tokens │   Out Tokens │   Cost($) │ Scores                                          │
├───────────────────────────┼─────────────────┼───────────────┼─────────────┼──────────────┼───────────┼─────────────────────────────────────────────────┤
│ Instruction Following     │ claude-sonnet-4 │        3605.8 │          52 │           53 │  0.000951 │ {'format_correct': True, 'no_extra_text': True} │
│ Instruction Following     │ gpt-4o          │        1651.3 │          49 │           14 │  0.000262 │ {'format_correct': True, 'no_extra_text': True} │
│ Context Fidelity (RAG sim │ claude-sonnet-4 │        1912.9 │         100 │           60 │  0.0012   │ manual review                                   │
│ Context Fidelity (RAG sim │ gpt-4o          │        1366.4 │          87 │           20 │  0.000418 │ manual review                                   │
│ Structured Output (JSON)  │ claude-sonnet-4 │        1909   │          70 │           50 │  0.00096  │ {'valid_json': True, 'has_all_fields': True}    │
│ Structured Output (JSON)  │ gpt-4o          │         784.3 │          71 │           31 │  0.000487 │ {'valid_json': True, 'has_all_fields': True}    │
│ Conciseness Under Constra │ claude-sonnet-4 │        3143.4 │          20 │           62 │  0.00099  │ {'word_count': 47, 'within_limit': True}        │
│ Conciseness Under Constra │ gpt-4o          │        1692   │          18 │           52 │  0.000565 │ {'word_count': 44, 'within_limit': True}        │
╰───────────────────────────┴─────────────────┴───────────────┴─────────────┴──────────────┴───────────┴─────────────────────────────────────────────────╯

📊 COST TOTALS (for these 4 test calls):
   Claude Sonnet 4: $0.004101
   GPT-4o:          $0.001733

⏱️  AVERAGE LATENCY:
   Claude Sonnet 4: 2643ms
   GPT-4o:          1374ms

🔭 SCALE PROJECTION (Apple-level: 50M requests/day):

   Claude Sonnet 4:
   Avg cost/call: $0.001025
   Daily (50M req): $51,262.50
   Monthly:         $1,537,875
   Annual:          $18,710,813

   GPT-4o:
   Avg cost/call: $0.000433
   Daily (50M req): $21,656.25
   Monthly:         $649,688
   Annual:          $7,904,531

✅ Benchmark complete. Review responses above for qualitative eval.