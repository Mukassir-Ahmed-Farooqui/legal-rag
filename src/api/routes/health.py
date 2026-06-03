from fastapi import APIRouter
from src.storage.qdrant_store import get_client
from src.models.responses import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Returns the health status of the API and its downstream dependencies (like Qdrant).
    """
    try:
        client = get_client()
        # Verify connectivity by listing collections
        client.get_collections()
        qdrant_status = "connected"
    except Exception as e:
        qdrant_status = f"disconnected: {str(e)}"

    return HealthResponse(
        status="ok" if "disconnected" not in qdrant_status else "degraded",
        version="0.1.0",
        qdrant_status=qdrant_status,
    )
