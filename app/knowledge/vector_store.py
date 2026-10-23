"""
ChromaDB vector store using Gemini embeddings.
No sentence-transformers, no PyTorch, no CUDA — pure API call.
Gemini embedding is free tier (1500 req/day).
"""
import json
import logging
from functools import lru_cache

import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from google import genai

from app.config import config
from app.knowledge.schemes import SCHEMES

logger = logging.getLogger(__name__)

COLLECTION_NAME = "setu_schemes"

# ── Gemini embedding function for ChromaDB ─────────────────────────────────────
class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self._client = genai.Client(api_key=config.GEMINI_API_KEY)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            try:
                result = self._client.models.embed_content(
                    model="models/text-embedding-004",
                    contents=text,
                )
                embeddings.append(result.embeddings[0].values)
            except Exception as e:
                logger.error("Gemini embedding error: %s", e)
                # Return zero vector as fallback (768 dims for text-embedding-004)
                embeddings.append([0.0] * 768)
        return embeddings


def _build_document(scheme: dict) -> str:
    return (
        f"Scheme: {scheme['scheme_name']}\n"
        f"Category: {scheme['category']}\n"
        f"State/National: {scheme['state_or_national']}\n"
        f"Eligibility: {scheme['eligibility']}\n"
        f"Benefits: {scheme['benefits']}\n"
        f"Documents: {', '.join(scheme['required_documents'])}\n"
        f"Steps: {' '.join(scheme['application_steps'])}\n"
        f"Department: {scheme['responsible_department']}\n"
        f"URL: {scheme['official_application_url']}\n"
    )


@lru_cache(maxsize=1)
def get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
    ef = GeminiEmbeddingFunction()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() == 0:
        logger.info("Seeding vector store with %d scheme records…", len(SCHEMES))
        documents = [_build_document(s) for s in SCHEMES]
        metadatas = [
            {
                "scheme_name": s["scheme_name"],
                "category": s["category"],
                "state_or_national": s["state_or_national"],
                "official_application_url": s["official_application_url"],
                "source_url": s["source_url"],
                "last_verified_date": s["last_verified_date"],
                "full_record": json.dumps(s, ensure_ascii=False),
            }
            for s in SCHEMES
        ]
        ids = [f"scheme_{i}" for i in range(len(SCHEMES))]
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        logger.info("Vector store seeded.")

    return collection


def retrieve_schemes(query: str, n_results: int = 3) -> list[dict]:
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["metadatas", "distances"],
    )
    schemes = []
    for meta in results["metadatas"][0]:
        try:
            schemes.append(json.loads(meta["full_record"]))
        except Exception:
            logger.warning("Failed to parse scheme record.")
    return schemes
