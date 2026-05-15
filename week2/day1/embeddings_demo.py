"""
embeddings_demo.py
Demonstrates how text gets converted to vectors and how
similar meanings produce similar vectors.
"""

import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    """Convert a piece of text into a vector (list of numbers).
    
    This is the foundation of RAG — we need to represent text
    as numbers so we can mathematically compare meanings.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",  # OpenAI's compact embedding model
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(vec_a, vec_b):
    """Measure how similar two vectors are (1.0 = identical, 0.0 = unrelated).
    
    This is the math behind 'find me the most relevant document.'
    Higher score = more semantically similar.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = sum(a ** 2 for a in vec_a) ** 0.5
    magnitude_b = sum(b ** 2 for b in vec_b) ** 0.5
    return dot_product / (magnitude_a * magnitude_b)

# --- Test with 4 sentences ---
sentences = [
    "The dog chased the ball in the park",
    "A puppy ran after a toy outside",          # Similar meaning to sentence 1
    "Apple released a new MacBook Pro",          # Different topic
    "The quarterly revenue exceeded expectations" # Very different topic
]

print("Generating embeddings for 4 sentences...\n")
embeddings = [get_embedding(s) for s in sentences]

# Show embedding dimensions — each sentence becomes a list of 1536 numbers
print(f"Each embedding has {len(embeddings[0])} dimensions")
print(f"First 5 values of sentence 1: {embeddings[0][:5]}\n")

# Compare all pairs
print("--- Similarity Scores ---")
print("(1.0 = identical meaning, closer to 0 = unrelated)\n")
for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        sim = cosine_similarity(embeddings[i], embeddings[j])
        print(f"  {sim:.3f}  |  \"{sentences[i][:40]}...\"")
        print(f"         vs \"{sentences[j][:40]}...\"\n")