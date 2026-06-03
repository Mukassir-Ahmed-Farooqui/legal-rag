import hashlib
import os
from dataclasses import asdict
from typing import Union

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)
from tqdm import tqdm

from src.ingestion.chunker import SectionChunk, SentenceChunk

load_dotenv()

COLLECTION_SECTIONS = "legal_sections"
COLLECTION_SENTENCES = "legal_sentences"
VECTOR_DIM = 384
BATCH_SIZE = 64
BGE_MODEL = "BAAI/bge-small-en-v1.5"

_DOC_PREFIX = "Represent this sentence: "
_QUERY_PREFIX = "Represent this question for searching relevant passages: "


def get_client() -> QdrantClient:
    return QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY") or None,
        timeout=60,
    )


def get_embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(BGE_MODEL)


def init_collections(client: QdrantClient, recreate: bool = False) -> None:
    existing = {c.name for c in client.get_collections().collections}

    for name in (COLLECTION_SECTIONS, COLLECTION_SENTENCES):
        if name in existing:
            if recreate:
                client.delete_collection(name)
            else:
                continue

        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=VECTOR_DIM,
                distance=Distance.COSINE,
            ),
        )

    for field_name in ("section_id", "doc_id"):
        client.create_payload_index(
            collection_name=COLLECTION_SENTENCES,
            field_name=field_name,
            field_schema=PayloadSchemaType.KEYWORD,
        )

    client.create_payload_index(
        collection_name=COLLECTION_SECTIONS,
        field_name="doc_id",
        field_schema=PayloadSchemaType.KEYWORD,
    )


def _chunk_to_point(
    chunk: Union[SectionChunk, SentenceChunk],
    vector: list[float],
) -> PointStruct:
    payload = asdict(chunk)
    point_id = int(
        hashlib.md5(chunk.chunk_id.encode()).hexdigest()[:15],
        16,
    )

    return PointStruct(
        id=point_id,
        vector=vector,
        payload=payload,
    )


def _embed(
    model,
    texts: list[str],
) -> list[list[float]]:
    prefixed = [_DOC_PREFIX + text for text in texts]

    return model.encode(
        prefixed,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()


def upsert_chunks(
    client: QdrantClient,
    model,
    chunks: list[Union[SectionChunk, SentenceChunk]],
    collection_name: str,
) -> int:
    total = 0

    for i in tqdm(
        range(0, len(chunks), BATCH_SIZE),
        desc=f"→ {collection_name}",
    ):
        batch = chunks[i : i + BATCH_SIZE]

        vectors = _embed(
            model,
            [c.text for c in batch],
        )

        points = [
            _chunk_to_point(c, v)
            for c, v in zip(batch, vectors)
        ]

        client.upsert(
            collection_name=collection_name,
            points=points,
        )

        total += len(points)

    return total


def embed_query(
    model,
    query: str,
) -> list[float]:
    return model.encode(
        _QUERY_PREFIX + query,
        normalize_embeddings=True,
    ).tolist()