import anthropic
import json
import time
from cost_calculator import count_tokens, estimate_cost

client = anthropic.Anthropic()

# ============================================================
# STRATEGY 1: FULL HISTORY (Naive Approach)
# Send the entire conversation every time.
# Pros: Perfect recall. Cons: Cost and latency grow linearly with conversation length.
# ============================================================

class FullHistoryMemory:
    """
    Simplest possible approach: append every message and resend everything.
    Good for: Short conversations, prototypes, high-stakes accuracy needs.
    Bad for: Long sessions, cost-sensitive products, latency-sensitive UX.
    """
    
    def __init__(self):
        self.history = []  # List of {"role": "user/assistant", "content": "..."}
    
    def chat(self, user_message: str) -> dict:
        # Add user's message to history
        self.history.append({"role": "user", "content": user_message})
        
        # Count tokens BEFORE sending — good engineering practice
        full_context = json.dumps(self.history)
        input_tokens = count_tokens(full_context)
        
        # Send entire history to API
        start_time = time.time()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # Haiku = fast + cheap, good for testing
            max_tokens=300,
            messages=self.history
        )
        latency_ms = (time.time() - start_time) * 1000
        
        assistant_message = response.content[0].text
        
        # Add response to history so next turn includes it
        self.history.append({"role": "assistant", "content": assistant_message})
        
        cost = estimate_cost(input_tokens, 100, "claude-haiku")
        
        return {
            "response":     assistant_message,
            "input_tokens": input_tokens,
            "cost":         cost["total_cost"],
            "latency_ms":   round(latency_ms, 1),
            "strategy":     "full_history"
        }


# ============================================================
# STRATEGY 2: SLIDING WINDOW
# Keep only the last N turns. Older context is dropped.
# Pros: Predictable cost/latency. Cons: Loses early context.
# ============================================================

class SlidingWindowMemory:
    """
    Keep only the most recent N exchanges.
    Like a goldfish with a configurable memory span.
    Good for: Customer support, simple Q&A, cost-controlled products.
    Bad for: Long research sessions, tasks referencing early context.
    """
    
    def __init__(self, window_size: int = 4):
        # window_size = number of TURNS to keep (1 turn = 1 user + 1 assistant message)
        self.window_size = window_size
        self.history = []
    
    def chat(self, user_message: str) -> dict:
        self.history.append({"role": "user", "content": user_message})
        
        # Trim to window: keep only last (window_size * 2) messages
        # *2 because each turn has a user message AND an assistant message
        windowed = self.history[-(self.window_size * 2):]
        
        input_tokens = count_tokens(json.dumps(windowed))
        
        start_time = time.time()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=windowed  # Only send the window, not full history
        )
        latency_ms = (time.time() - start_time) * 1000
        
        assistant_message = response.content[0].text
        self.history.append({"role": "assistant", "content": assistant_message})
        
        cost = estimate_cost(input_tokens, 100, "claude-haiku")
        
        return {
            "response":     assistant_message,
            "input_tokens": input_tokens,
            "cost":         cost["total_cost"],
            "latency_ms":   round(latency_ms, 1),
            "strategy":     f"sliding_window_{self.window_size}"
        }


# ============================================================
# STRATEGY 3: SUMMARIZATION MEMORY
# Compress old history into a running summary. Keep recent turns verbatim.
# Pros: Retains gist of full conversation at lower token cost.
# Cons: Lossy — nuance can be lost in summarization.
# ============================================================

class SummarizationMemory:
    """
    After N turns, ask the model to summarize older history.
    Store the summary + recent verbatim messages.
    Good for: Long sessions where full recall matters but cost is a concern.
    Bad for: When exact earlier wording matters (e.g., legal, technical specs).
    """
    
    def __init__(self, summarize_after: int = 4):
        # How many turns before we summarize old ones
        self.summarize_after = summarize_after
        self.summary = ""       # Compressed representation of older history
        self.recent = []        # Last few turns kept verbatim
    
    def _summarize(self) -> str:
        """
        Ask Claude to compress the recent history into a summary paragraph.
        This is a separate API call — note: adds latency and cost at summarization time.
        """
        if not self.recent:
            return self.summary
        
        # Build a prompt asking for compression
        history_text = "\n".join([
            f"{m['role'].upper()}: {m['content']}" 
            for m in self.recent
        ])
        
        prompt = f"""Previous conversation summary:
{self.summary}

Recent conversation:
{history_text}

Write a concise 2-3 sentence summary capturing the key facts, decisions, and context from this conversation. Focus on information the user might reference later."""
        
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def chat(self, user_message: str) -> dict:
        self.recent.append({"role": "user", "content": user_message})
        
        # When we've accumulated enough turns, compress the older ones
        if len(self.recent) > self.summarize_after * 2:
            self.summary = self._summarize()
            # Keep only the last 2 turns verbatim; rest is now in summary
            self.recent = self.recent[-4:]
        
        # Build messages: summary as context + recent verbatim
        messages = []
        if self.summary:
            # Inject summary as a system-level reminder at the start
            messages.append({
                "role": "user",
                "content": f"[Conversation context: {self.summary}]"
            })
            messages.append({
                "role": "assistant", 
                "content": "Understood, I have context from our earlier conversation."
            })
        messages.extend(self.recent)
        
        input_tokens = count_tokens(json.dumps(messages))
        
        start_time = time.time()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=messages
        )
        latency_ms = (time.time() - start_time) * 1000
        
        assistant_message = response.content[0].text
        self.recent.append({"role": "assistant", "content": assistant_message})
        
        cost = estimate_cost(input_tokens, 100, "claude-haiku")
        
        return {
            "response":     assistant_message,
            "input_tokens": input_tokens,
            "cost":         cost["total_cost"],
            "latency_ms":   round(latency_ms, 1),
            "strategy":     "summarization"
        }


# ============================================================
# COMPARISON RUNNER
# Run all three strategies through the same conversation
# and compare the metrics side by side.
# ============================================================

def run_comparison():
    """
    Send identical multi-turn conversations through all three strategies.
    Print token counts, costs, and latencies at each turn.
    This is your benchmark — the numbers you'll cite in interviews.
    """
    
    # A realistic support-style conversation that builds context over time
    conversation = [
        "Hi! I'm planning a trip to Japan in April.",
        "I want to visit Tokyo and Kyoto. Which should I start with?",
        "I have about 10 days total. How should I split my time?",
        "What's the best way to get between those cities?",
        "Going back to my trip — what did I say my travel month was?",  # Tests memory recall
    ]
    
    strategies = {
        "Full History":    FullHistoryMemory(),
        "Sliding Window":  SlidingWindowMemory(window_size=2),
        "Summarization":   SummarizationMemory(summarize_after=2),
    }
    
    results = {name: [] for name in strategies}
    
    print("=" * 65)
    print("MEMORY STRATEGY COMPARISON")
    print("=" * 65)
    
    for turn_num, user_msg in enumerate(conversation, 1):
        print(f"\n--- Turn {turn_num}: '{user_msg[:50]}...' ---")
        
        for strategy_name, strategy_obj in strategies.items():
            result = strategy_obj.chat(user_msg)
            results[strategy_name].append(result)
            
            print(f"  [{strategy_name:15}] "
                  f"tokens={result['input_tokens']:4d} | "
                  f"cost=${result['cost']:.5f} | "
                  f"{result['latency_ms']:5.0f}ms")
    
    # Summary: Total cost per strategy across all turns
    print("\n" + "=" * 65)
    print("TOTAL COST ACROSS ALL TURNS")
    print("=" * 65)
    for strategy_name, turn_results in results.items():
        total_cost   = sum(r["cost"] for r in turn_results)
        total_tokens = sum(r["input_tokens"] for r in turn_results)
        avg_latency  = sum(r["latency_ms"] for r in turn_results) / len(turn_results)
        print(f"  {strategy_name:20}: "
              f"${total_cost:.4f} total | "
              f"{total_tokens:5d} tokens | "
              f"{avg_latency:.0f}ms avg latency")
    
    # Check if the memory strategies actually recalled the month
    print("\n" + "=" * 65)
    print("MEMORY RECALL TEST (Turn 5 — 'What month did I say?')")
    print("=" * 65)
    for strategy_name, turn_results in results.items():
        response = turn_results[4]["response"]  # Turn 5 = index 4
        recalled = "april" in response.lower()
        print(f"  {strategy_name:20}: {'✅ Recalled April' if recalled else '❌ Forgot'}")
        print(f"    Response: {response[:100]}...")

if __name__ == "__main__":
    run_comparison()