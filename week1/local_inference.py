import requests
import json
import time

# Ollama runs on localhost:11434 by default
OLLAMA_API = "http://localhost:11434/api/generate"

def inference_local(prompt: str, model: str = "llama2") -> dict:
    """
    Call a local LLM via Ollama.
    
    Returns: {
        'response': str (the model's output),
        'latency_ms': float (how long it took)
    }
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,  # Wait for full response before returning
        "temperature": 0.7  # Balance creativity and consistency
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(OLLAMA_API, json=payload)
        response.raise_for_status()
        
        latency_ms = (time.time() - start_time) * 1000
        result = response.json()
        
        return {
            "response": result.get("response", "").strip(),
            "latency_ms": round(latency_ms, 1),
            "model": model
        }
    
    except requests.exceptions.ConnectionError:
        return {
            "error": "Ollama not running. Run: ollama run llama2",
            "latency_ms": 0
        }

# Test it
if __name__ == "__main__":
    prompts = [
        "What is RAG (Retrieval-Augmented Generation)?",
        "Explain embeddings in 1 sentence.",
        "Why would Apple use local LLMs?"
    ]
    
    for prompt in prompts:
        print(f"\n📝 Prompt: {prompt}")
        result = inference_local(prompt)
        
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"Response: {result['response'][:150]}...")
            print(f"⏱️  Latency: {result['latency_ms']}ms")