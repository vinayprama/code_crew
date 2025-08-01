from sentence_transformers import SentenceTransformer
from functools import lru_cache

model = SentenceTransformer('all-MiniLM-L6-v2')  # Dim = 384

@lru_cache(maxsize=256)
def embed_text(text: str):
    """Convert text into embedding vector with caching."""
    return model.encode(text).tolist()
