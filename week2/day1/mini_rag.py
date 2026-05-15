"""
mini_rag.py
A complete RAG pipeline in ~80 lines.
This is the same architecture (simplified) behind Apple Intelligence's
on-device document retrieval and most enterprise AI search products.

RAG = Retrieval-Augmented Generation: we don't stuff everything into the
LLM's context. Instead, we search for relevant chunks first, then only
send those to the model. Cheaper, faster, and more accurate for factual Q&A.
"""

import chromadb
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI client for both embeddings (text→vectors) and chat (answer generation)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =====================================================
# STAGE 0: PREPARE THE KNOWLEDGE BASE
# In production, this would be thousands of documents chunked from
# PDFs, wikis, or help articles. Here we simulate a product knowledge base.
# Each string = one "chunk" — a self-contained unit of information.
# =====================================================

documents = [
    # Chunk 0: Pricing
    "PhotoSync Pro costs $9.99/month or $79.99/year for individual plans. "
    "Team plans start at $14.99/user/month with a minimum of 5 users.",
    # Chunk 1: Privacy / on-device
    "PhotoSync Pro uses on-device AI to automatically tag and organize photos. "
    "Face recognition runs entirely on the user's device for privacy. "
    "Only encrypted metadata is synced to the cloud.",
    # Chunk 2: File formats
    "PhotoSync Pro supports JPEG, PNG, HEIC, RAW (CR3, ARW, NEF), and TIFF formats. "
    "Video support includes MP4, MOV, and ProRes up to 8K resolution.",
    # Chunk 3: Hardware requirements
    "The AI photo search feature requires iOS 17+ or macOS Sonoma+. "
    "On-device processing needs Apple Silicon (M1 or later) or A15 chip or later. "
    "Older devices fall back to cloud-based processing.",
    # Chunk 4: Smart Albums
    "PhotoSync Pro's Smart Albums use machine learning to group photos by event, "
    "location, and people. The model updates weekly based on new photos added. "
    "Users can correct groupings to improve accuracy over time.",
    # Chunk 5: Data export
    "Data export is available in standard formats. Users can export their entire "
    "library including AI-generated tags and albums. We support Google Takeout "
    "format for easy migration. No vendor lock-in.",
]

# =====================================================
# STAGE 1: EMBED & STORE (happens once, or when docs change)
# Embeddings turn text into vectors (lists of numbers). Semantically
# similar text → similar vectors. That's how we search by meaning,
# not just keyword matching.
# =====================================================

print("Setting up vector database...")

# ChromaDB = in-memory vector DB. No server, no setup. For production,
# you'd use chromadb.PersistentClient(path="...") to save to disk.
chroma_client = chromadb.Client()

# A collection is like a table. "cosine" similarity = standard for
# comparing embedding vectors (angle between them, 0° = identical).
collection = chroma_client.create_collection(
    name="product_docs",
    metadata={"hnsw:space": "cosine"}
)

# We use OpenAI embeddings (not ChromaDB's default) for higher quality.
# text-embedding-3-small outputs 1536-dimensional vectors.
def embed_texts(texts):
    """Batch-embed multiple texts using OpenAI's embedding model."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]

# Convert all chunks to vectors in one API call (batch = cheaper)
doc_embeddings = embed_texts(documents)

# Persist to ChromaDB: each doc gets an ID so we can retrieve it later.
# ChromaDB will use these embeddings for similarity search.
collection.add(
    documents=documents,
    embeddings=doc_embeddings,
    ids=[f"doc_{i}" for i in range(len(documents))]
)
print(f"Indexed {len(documents)} document chunks.\n")

# =====================================================
# STAGE 2 & 3: RETRIEVE & AUGMENT
# At query time: embed the question → find similar chunks → pass them
# to the LLM as context. The model answers from context, not memory.
# =====================================================

def ask(question, n_results=2):
    """Full RAG pipeline: embed question → retrieve → generate answer.
    
    n_results: how many chunks to fetch. 2–3 is usually enough; more
    can add noise or exceed context limits for long documents.
    """
    # Step 1: Embed the question (same model as docs = comparable vectors)
    q_embedding = embed_texts([question])[0]
    
    # Step 2: Vector similarity search — ChromaDB returns chunks whose
    # embeddings are closest to the question's embedding.
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=n_results
    )
    
    # results["documents"] is a list of lists (one per query); we have 1 query
    context_chunks = results["documents"][0]
    
    # Step 3: "Augment" = inject retrieved chunks into the prompt.
    # The LLM sees only this context, so it can't hallucinate from training.
    context = "\n\n".join(context_chunks)
    
    prompt = f"""Answer the user's question using ONLY the provided context.
If the context doesn't contain the answer, say "I don't have that information."

Context:
{context}

Question: {question}

Answer:"""
    
    # Step 4: Call the LLM with our augmented prompt. The model never
    # saw the full knowledge base — only the 2 chunks we retrieved.
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Fast and cheap; gpt-4o for harder reasoning
        messages=[{"role": "user", "content": prompt}],
        temperature=0  # Deterministic — same question → same answer
    )
    
    answer = response.choices[0].message.content
    
    # Debug output: see which chunks were retrieved and why
    print(f"Q: {question}")
    print(f"\n📎 Retrieved chunks:")
    for i, chunk in enumerate(context_chunks):
        print(f"   [{i+1}] {chunk[:80]}...")
    print(f"\n💬 Answer: {answer}\n")
    print("-" * 60 + "\n")
    
    return answer

# =====================================================
# TEST IT: Ask questions that exercise different retrieval paths
# =====================================================

# Single-chunk retrieval: pricing doc
ask("How much does PhotoSync Pro cost?")

# Single-chunk: privacy/on-device doc
ask("How does PhotoSync Pro handle user privacy?")

# Semantic match: "Canon RAW" → format support doc (CR3, RAW)
ask("Can I use RAW photos from my Canon camera?")

# Out-of-scope: tests grounding — answer not in docs → "I don't know"
ask("Does PhotoSync Pro have an Android app?")

# Multi-chunk: needs hardware (iOS 17, Apple Silicon) + pricing
ask("What hardware do I need for AI features, and how much does it cost?")