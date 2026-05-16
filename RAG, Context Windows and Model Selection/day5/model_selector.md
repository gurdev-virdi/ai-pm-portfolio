
📱 SCENARIO 1: Siri on-device quick reply suggestions

=================================================================
MODEL SELECTION RECOMMENDATION
=================================================================
Requirements: latency≤150ms | cost≤$0.0/1K | privacy=True | complexity=simple

✅ RECOMMENDED MODELS:

  Apple Intelligence (on-device) (Apple)
  Apple Intelligence small model. Ideal for real-time features.
    ✓ Latency 80ms ≤ budget 150ms
    ✓ Cost $0.0/1K ≤ budget $0.0/1K
    ✓ Privacy-safe deployment
    ✓ Context 4096 ≥ required 2048
    ✓ Handles 'simple' complexity

=================================================================

📄 SCENARIO 2: Apple Intelligence writing tools (longer docs)

=================================================================
MODEL SELECTION RECOMMENDATION
=================================================================
Requirements: latency≤2000ms | cost≤$0.1/1K | privacy=True | complexity=complex

✅ RECOMMENDED MODELS:

  Apple Private Cloud Compute (Apple)
  For complex tasks that exceed on-device capability. Privacy preserved.
    ✓ Latency 600ms ≤ budget 2000ms
    ✓ Cost $0.0/1K ≤ budget $0.1/1K
    ✓ Privacy-safe deployment
    ✓ Context 32000 ≥ required 16000
    ✓ Handles 'complex' complexity

=================================================================

🔍 SCENARIO 3: Third-party app using Apple AI APIs (developer tool)

=================================================================
MODEL SELECTION RECOMMENDATION
=================================================================
Requirements: latency≤3000ms | cost≤$0.05/1K | privacy=False | complexity=moderate

✅ RECOMMENDED MODELS:

  Apple Private Cloud Compute (Apple)
  For complex tasks that exceed on-device capability. Privacy preserved.
    ✓ Latency 600ms ≤ budget 3000ms
    ✓ Cost $0.0/1K ≤ budget $0.05/1K
    ✓ Context 32000 ≥ required 8000
    ✓ Handles 'moderate' complexity

  claude-3-5-haiku (Anthropic)
  Fast, cheap Claude. Best for high-volume moderate tasks.
    ✓ Latency 800ms ≤ budget 3000ms
    ✓ Cost $0.0056/1K ≤ budget $0.05/1K
    ✓ Context 200000 ≥ required 8000
    ✓ Handles 'moderate' complexity

  gpt-4o-mini (OpenAI)
  Cheapest capable cloud model. OpenAI data retention applies.
    ✓ Latency 700ms ≤ budget 3000ms
    ✓ Cost $0.00048/1K ≤ budget $0.05/1K
    ✓ Context 128000 ≥ required 8000
    ✓ Handles 'moderate' complexity

  gpt-4o (OpenAI)
  High quality, multimodal. Consider for vision tasks.
    ✓ Latency 2000ms ≤ budget 3000ms
    ✓ Cost $0.045/1K ≤ budget $0.05/1K
    ✓ Context 128000 ≥ required 8000
    ✓ Handles 'moderate' complexity
