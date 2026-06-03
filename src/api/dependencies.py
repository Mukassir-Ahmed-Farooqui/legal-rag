from functools import lru_cache
from src.chain import LegalRAG


@lru_cache(maxsize=1)
def get_rag_pipeline() -> LegalRAG:
    """
    Returns a cached, singleton instance of LegalRAG.
    This avoids reloading the heavy SentenceTransformer model on every API request.
    """
    return LegalRAG()
