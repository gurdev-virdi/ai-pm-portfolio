"""
chunking_compare.py
Compare 3 chunking strategies on the same document.
Shows why chunking is the #1 decision in RAG quality.
"""

from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

# A realistic product document — notice how topics flow into each other
PRODUCT_DOC = """
PhotoSync Pro - Product Overview

Pricing and Plans
PhotoSync Pro is available in three tiers. The Free tier includes 5GB storage and basic photo organization. The Pro tier costs $9.99/month or $79.99/year and includes unlimited storage, AI-powered tagging, and Smart Albums. The Team tier starts at $14.99/user/month with a minimum of 5 users and adds shared libraries, admin controls, and priority support.

All paid plans include a 14-day free trial. Annual plans save 33% compared to monthly billing. Students and educators get 50% off with a valid .edu email address.

Privacy and Security
PhotoSync Pro takes a privacy-first approach inspired by Apple's design philosophy. All face recognition and photo tagging happens on-device using Core ML models optimized for Apple Silicon. Only encrypted metadata is synced to iCloud for cross-device access.

For Team plans, administrators can configure data residency requirements. Enterprise customers can choose between US, EU, and APAC data centers. SOC 2 Type II certification was completed in January 2026.

Photos are encrypted at rest using AES-256 and in transit using TLS 1.3. Users can enable end-to-end encryption for an additional layer of protection, though this disables some cloud-based features like shared albums.

AI Features and Requirements
The AI photo search feature uses a multimodal model that understands both image content and natural language queries. Users can search for "sunset at the beach with Sarah" and get accurate results even without manual tags.

Smart Albums use on-device machine learning to automatically group photos by event, location, season, and people. The grouping model retrains weekly using federated learning — the model improves from usage patterns without any raw photos leaving the device.

AI features require iOS 17+ or macOS Sonoma+ with Apple Silicon (M1/A15 or later). Older devices fall back to cloud-based processing with slightly higher latency (200-500ms vs 50-100ms on-device). Users on older hardware can disable AI features to save battery.

The AI model is approximately 450MB and downloads on first use over Wi-Fi. Subsequent model updates are delta updates averaging 15-30MB.
"""

# =====================================================
# STRATEGY 1: Fixed-size chunking
# Splits every N characters regardless of content.
# Simple but dumb — will cut mid-sentence.
# =====================================================

fixed_splitter = CharacterTextSplitter(
    separator="",           # Split on any character boundary
    chunk_size=300,         # ~75 words per chunk
    chunk_overlap=0,        # No overlap between chunks
)
fixed_chunks = fixed_splitter.split_text(PRODUCT_DOC)

# =====================================================
# STRATEGY 2: Recursive chunking (industry standard)
# Tries paragraph breaks first, then sentences, then words.
# Respects natural document structure.
# =====================================================

recursive_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " "],  # Try these in order
    chunk_size=400,          # ~100 words per chunk
    chunk_overlap=50,        # 50-char overlap catches split context
)
recursive_chunks = recursive_splitter.split_text(PRODUCT_DOC)

# =====================================================
# STRATEGY 3: Recursive with larger chunks + more overlap
# For complex docs where context spans paragraphs.
# Trades cost (more tokens) for better context retention.
# =====================================================

large_recursive_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " "],
    chunk_size=800,          # ~200 words — keeps more context
    chunk_overlap=200,       # Big overlap ensures no info is lost at boundaries
)
large_chunks = large_recursive_splitter.split_text(PRODUCT_DOC)

# =====================================================
# COMPARE RESULTS
# =====================================================

def show_chunks(name, chunks):
    print(f"\n{'='*60}")
    print(f"  {name}: {len(chunks)} chunks")
    print(f"{'='*60}")
    for i, chunk in enumerate(chunks):
        # Show first 100 chars of each chunk
        preview = chunk.strip().replace('\n', ' ')[:100]
        print(f"  [{i+1}] ({len(chunk)} chars) {preview}...")
    print()

show_chunks("FIXED (300 chars, no overlap)", fixed_chunks)
show_chunks("RECURSIVE (400 chars, 50 overlap)", recursive_chunks)
show_chunks("LARGE RECURSIVE (800 chars, 200 overlap)", large_chunks)

# =====================================================
# THE KEY QUESTION: Which strategy retrieves the right
# chunk for a given query?
# =====================================================

print("\n" + "="*60)
print("  RETRIEVAL TEST")
print("="*60)

test_query = "How much does PhotoSync Pro cost for students?"
print(f"\n  Query: \"{test_query}\"")
print(f"\n  The correct answer spans TWO pieces of info:")
print(f"  1. Pro tier = $9.99/month")
print(f"  2. Students get 50% off with .edu email")
print()

# Check which strategy has BOTH facts in a single chunk
for name, chunks in [
    ("Fixed", fixed_chunks),
    ("Recursive", recursive_chunks),
    ("Large Recursive", large_chunks),
]:
    for i, chunk in enumerate(chunks):
        has_price = "9.99" in chunk
        has_student = "student" in chunk.lower() or ".edu" in chunk.lower()
        if has_price or has_student:
            both = "✅ BOTH facts" if (has_price and has_student) else "⚠️ partial"
            print(f"  {name} chunk [{i+1}]: {both}")
            print(f"    price={'9.99' in chunk}  student={'student' in chunk.lower() or '.edu' in chunk.lower()}")
