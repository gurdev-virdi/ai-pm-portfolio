"""
retrieval_eval.py
Measure how well our RAG retrieval actually works.
This is the #1 eval every AI PM should know how to run.

Two key metrics:
- Hit Rate: Did the correct chunk appear in our top-K results?
- MRR (Mean Reciprocal Rank): How high did the correct chunk rank?
"""

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import chromadb
import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# KNOWLEDGE BASE — same product docs, chunked well
# =====================================================

chunks = [
    {"id": "pricing",
     "text": "PhotoSync Pro is available in three tiers. The Free tier includes 5GB storage and basic photo organization. The Pro tier costs $9.99/month or $79.99/year and includes unlimited storage, AI-powered tagging, and Smart Albums. The Team tier starts at $14.99/user/month with a minimum of 5 users. All paid plans include a 14-day free trial. Annual plans save 33%. Students and educators get 50% off with a valid .edu email address."},
    
    {"id": "privacy",
     "text": "PhotoSync Pro takes a privacy-first approach. All face recognition and photo tagging happens on-device using Core ML models optimized for Apple Silicon. Only encrypted metadata is synced to iCloud. Photos are encrypted at rest using AES-256 and in transit using TLS 1.3. Users can enable end-to-end encryption for additional protection."},
    
    {"id": "ai_features",
     "text": "The AI photo search uses a multimodal model that understands both image content and natural language queries. Smart Albums use on-device machine learning to group photos by event, location, season, and people. The model retrains weekly using federated learning without raw photos leaving the device."},
    
    {"id": "requirements",
     "text": "AI features require iOS 17+ or macOS Sonoma+ with Apple Silicon (M1/A15 or later). Older devices fall back to cloud-based processing with 200-500ms latency vs 50-100ms on-device. The AI model is approximately 450MB and downloads on first use over Wi-Fi."},
    
    {"id": "team_features",
     "text": "For Team plans, administrators can configure data residency requirements. Enterprise customers can choose between US, EU, and APAC data centers. SOC 2 Type II certification was completed in January 2026. Shared libraries and admin controls are included."},
    
    {"id": "formats",
     "text": "PhotoSync Pro supports JPEG, PNG, HEIC, RAW (CR3, ARW, NEF), and TIFF formats. Video support includes MP4, MOV, and ProRes up to 8K resolution. Data export is available in standard formats including Google Takeout for easy migration."},
]

# =====================================================
# SET UP VECTOR DATABASE
# =====================================================

def embed_texts(texts):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(
    name="eval_docs",
    metadata={"hnsw:space": "cosine"}
)

# Index all chunks
all_texts = [c["text"] for c in chunks]
all_embeddings = embed_texts(all_texts)
all_ids = [c["id"] for c in chunks]

collection.add(
    documents=all_texts,
    embeddings=all_embeddings,
    ids=all_ids
)

# =====================================================
# EVALUATION DATASET
# Each test case: a question + the chunk ID that should
# be retrieved. This is your "ground truth."
# 
# Writing these test cases is a core AI PM skill.
# =====================================================

eval_set = [
    # Straightforward matches
    {"query": "How much does PhotoSync Pro cost?",
     "expected_id": "pricing",
     "difficulty": "easy"},
    
    {"query": "Is my data encrypted?",
     "expected_id": "privacy",
     "difficulty": "easy"},
    
    {"query": "What file types are supported?",
     "expected_id": "formats",
     "difficulty": "easy"},
    
    # Phrased differently from the document
    {"query": "Can I use this on my old iPhone?",
     "expected_id": "requirements",
     "difficulty": "medium"},
    
    {"query": "How does the app protect my photos?",
     "expected_id": "privacy",
     "difficulty": "medium"},
    
    {"query": "Is there a discount for my university?",
     "expected_id": "pricing",
     "difficulty": "medium"},
    
    # Requires understanding intent, not keyword matching
    {"query": "Will it work offline?",
     "expected_id": "requirements",
     "difficulty": "hard"},
    
    {"query": "Can my company control where data is stored?",
     "expected_id": "team_features",
     "difficulty": "hard"},
    
    {"query": "How smart is the search?",
     "expected_id": "ai_features",
     "difficulty": "hard"},
    
    {"query": "I shoot Canon RAW, will those import?",
     "expected_id": "formats",
     "difficulty": "hard"},
]

# =====================================================
# RUN THE EVALUATION
# =====================================================

def evaluate_retrieval(eval_set, top_k=3):
    """
    Run all test queries and compute retrieval metrics.
    
    Hit Rate @ K: What % of queries had the correct chunk in top K?
    MRR (Mean Reciprocal Rank): Average of 1/rank of the correct chunk.
      - MRR=1.0 means the right chunk was always #1
      - MRR=0.5 means it was typically #2
    """
    hits = 0
    reciprocal_ranks = []
    results_detail = []
    
    # Embed all queries in one batch (cheaper and faster)
    all_queries = [e["query"] for e in eval_set]
    query_embeddings = embed_texts(all_queries)
    
    for i, test_case in enumerate(eval_set):
        # Retrieve top K chunks
        results = collection.query(
            query_embeddings=[query_embeddings[i]],
            n_results=top_k
        )
        
        retrieved_ids = results["ids"][0]
        expected = test_case["expected_id"]
        
        # Check: is the correct chunk in our results?
        if expected in retrieved_ids:
            hits += 1
            rank = retrieved_ids.index(expected) + 1  # 1-indexed
            reciprocal_ranks.append(1.0 / rank)
            status = f"✅ Found at rank {rank}"
        else:
            reciprocal_ranks.append(0.0)
            status = f"❌ Not in top {top_k} (got: {retrieved_ids[:2]})"
        
        results_detail.append({
            "query": test_case["query"],
            "difficulty": test_case["difficulty"],
            "expected": expected,
            "status": status
        })
    
    # Print results
    print(f"\n{'='*60}")
    print(f"  RETRIEVAL EVALUATION (top_k={top_k})")
    print(f"{'='*60}\n")
    
    for r in results_detail:
        print(f"  [{r['difficulty']:6s}] {r['status']}")
        print(f"          Q: \"{r['query']}\"")
        print(f"          Expected: {r['expected']}\n")
    
    hit_rate = hits / len(eval_set)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
    
    print(f"  {'─'*40}")
    print(f"  Hit Rate @ {top_k}: {hit_rate:.0%} ({hits}/{len(eval_set)})")
    print(f"  MRR:            {mrr:.3f}")
    print(f"  {'─'*40}")
    print()
    
    # Break down by difficulty
    for diff in ["easy", "medium", "hard"]:
        subset = [r for r, e in zip(reciprocal_ranks, eval_set) if e["difficulty"] == diff]
        if subset:
            print(f"  {diff:6s}: MRR = {sum(subset)/len(subset):.3f}")
    
    return hit_rate, mrr

# Run evals at different K values to see the tradeoff
print("\n🔍 Running retrieval evaluation...\n")
for k in [1, 2, 3]:
    evaluate_retrieval(eval_set, top_k=k)
