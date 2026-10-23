"""
ChromaDB vector store — builds and queries the scheme knowledge base.
Uses sentence-transformers for local free embeddings (no API calls).
"""
import json
import logging
from functools import lru_cache

import chromadb
from chromadb.utils import embedding_functions

from app.config import config
from app.knowledge.schemes import SCHEMES

logger = logging.getLogger(__name__)

COLLECTION_NAME = "setu_schemes"


def _build_document(scheme: dict) -> str:
    """Flatten a scheme record into a searchable text blob."""
    return (
        f"Scheme: {scheme['scheme_name']}\n"
        f"Category: {scheme['category']}\n"
        f"State/National: {scheme['state_or_national']}\n"
        f"Eligibility: {scheme['eligibility']}\n"
        f"Benefits: {scheme['benefits']}\n"
        f"Required Documents: {', '.join(scheme['required_documents'])}\n"
        f"Application Steps: {' '.join(scheme['application_steps'])}\n"
        f"Responsible Department: {scheme['responsible_department']}\n"
        f"Official URL: {scheme['official_application_url']}\n"
    )


@lru_cache(maxsize=1)
def get_collection() -> chromadb.Collection:
    """Initialise ChromaDB client and collection (cached — runs once)."""
    client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    # Seed with scheme data if collection is empty
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
                # Store full record as JSON for retrieval
                "full_record": json.dumps(s, ensure_ascii=False),
            }
            for s in SCHEMES
        ]
        ids = [f"scheme_{i}" for i in range(len(SCHEMES))]
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        logger.info("Vector store seeded successfully.")

    return collection


def retrieve_schemes(query: str, n_results: int = 3) -> list[dict]:
    """
    Semantic search — returns the top-n matching scheme records.
    Each returned dict is the full scheme record from SCHEMES.
    """
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["metadatas", "distances"],
    )

    schemes = []
    for meta in results["metadatas"][0]:
        try:
            record = json.loads(meta["full_record"])
            schemes.append(record)
        except Exception:
            logger.warning("Failed to deserialise scheme record from vector store.")
    return schemes
