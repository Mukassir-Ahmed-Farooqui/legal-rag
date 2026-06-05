import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import (
    query,
    health,
    upload,
    documents,
    auth,
    chats,
)


from contextlib import asynccontextmanager
from src.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto deploy database schemas on startup
    init_db()
    yield

app = FastAPI(
    title="Legal RAG API",
    description="API to query the legal documents retrieval-augmented generation (RAG) pipeline.",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes with API prefix
app.include_router(query.router, prefix="/api/v1/query", tags=["query"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(
    upload.router,
    prefix="/api/v1/upload",
    tags=["upload"],
)
app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["documents"],
)
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["auth"],
)
app.include_router(
    chats.router,
    prefix="/api/v1/chats",
    tags=["chats"],
)




@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Legal RAG API. Visit /docs for the API documentation."
    }


if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
