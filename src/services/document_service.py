from src.storage.qdrant_store import (
    get_client,
    COLLECTION_SECTIONS,
    COLLECTION_SENTENCES,
)
from qdrant_client.models import Filter, FieldCondition


def list_documents():
    client = get_client()

    records, _ = client.scroll(
        collection_name=COLLECTION_SECTIONS,
        limit=10000,
        with_payload=True,
    )

    docs = {}

    for point in records:
        payload = point.payload

        doc_id = payload.get("doc_id")
        filename = payload.get("filename", "")

        if doc_id not in docs:
            docs[doc_id] = {
                "doc_id": doc_id,
                "filename": filename,
            }

    return list(docs.values())


def delete_document(doc_id: str):

    client = get_client()

    doc_filter = Filter(
        must=[
            FieldCondition(
                key="doc_id",
                match={"value": doc_id},
            )
        ]
    )

    client.delete(
        collection_name=COLLECTION_SECTIONS,
        points_selector=doc_filter,
    )

    client.delete(
        collection_name=COLLECTION_SENTENCES,
        points_selector=doc_filter,
    )

    return {
        "status": "deleted",
        "doc_id": doc_id,
    }
