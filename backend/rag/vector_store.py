"""
RAG store for news/geopolitical context, backed by local ChromaDB with
sentence-transformers embeddings (fully free, runs locally, no API cost).

News Agent calls add_news() for every article it scrapes/fetches.
Recommendation Agent calls query() to retrieve relevant context before
asking the LLM to reason about a corridor/event.
"""
import os
import uuid
import chromadb
from chromadb.utils import embedding_functions
from utils.logger import get_logger

log = get_logger("vector_store")

_CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chroma")
os.makedirs(_CHROMA_PATH, exist_ok=True)

_client = chromadb.PersistentClient(path=_CHROMA_PATH)
_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
_collection = _client.get_or_create_collection(
    name="oil_news", embedding_function=_embed_fn
)


def add_news(text: str, metadata: dict) -> None:
    """metadata example: {"date": "2026-07-20", "corridor": "hormuz",
    "source": "reuters", "sentiment": "negative"}"""
    doc_id = str(uuid.uuid4())
    _collection.add(documents=[text], metadatas=[metadata], ids=[doc_id])
    log.info(f"[RAG] Indexed article ({metadata.get('corridor', 'unknown')} / "
              f"{metadata.get('source', 'unknown')})")


def query(question: str, k: int = 5, corridor: str | None = None) -> list[dict]:
    """Return top-k relevant chunks, optionally filtered by corridor."""
    where = {"corridor": corridor} if corridor else None
    results = _collection.query(query_texts=[question], n_results=k, where=where)
    hits = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    for doc, meta in zip(docs, metas):
        hits.append({"text": doc, "metadata": meta})
    log.info(f"[RAG] Retrieved {len(hits)} chunks for query: '{question[:60]}...'")
    return hits


def count() -> int:
    return _collection.count()
