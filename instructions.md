# Download and run Llama 2 7B (4.2GB, ~7min on decent internet)
ollama run llama2
```

This will take 7-10 minutes. While it downloads, read: https://ollama.ai/library

**What's happening:** Ollama is pulling the quantized model (4-bit precision = smaller files, less accuracy lost than you'd think).

Once it starts, you'll see a prompt:
```
Send a message (/help for more options, type 'quit' to exit)
>>>
```

**Type your first prompt:**
```
Explain why on-device AI is important for consumer products, in 2 sentences.
```

Wait for response. Notice the latency (will show at end: "X ms").

**Try 3 more prompts to get a feel:**
```
>>> What are the privacy implications of cloud AI?
>>> How many parameters does Llama 2 have?
>>> quit
```

**How to see latency:** The interactive `ollama run` CLI does not print timing. To measure it:

- **API (one-off):** `curl http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"Hi","stream":false}'` — response JSON includes `eval_duration`, `total_duration` (nanoseconds).
- **Benchmark:** `ollama bench llama2` — runs a short benchmark and reports tokens/sec and latency.