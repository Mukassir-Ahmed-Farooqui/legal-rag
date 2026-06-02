import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from groq import Groq

load_dotenv()

# --- 1. Load embedding model (runs locally, no API key needed) ---
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# --- 2. Your toy documents (3 sentences about a fake legal case) ---
docs = [
    """
    This residential lease shall remain in effect until the end of the calendar year 2025,
    at which point all obligations under the agreement will terminate unless renewed by both parties.
    """,

    """
    Tenants intending to leave the property are required to inform the landlord in writing
    no fewer than sixty (60) days prior to their planned move-out date.
    Failure to provide adequate notice may result in additional charges.
    """,

    """
    Rent payments are expected at the beginning of every month.
    Any payment received after the first business day may be considered late and subject
    to penalties outlined elsewhere in this agreement.
    """
]

# --- 3. Embed all docs ---
embeddings = model.encode(docs)
print(f"Each vector has {len(embeddings[0])} dimensions")

# --- 4. Store in Qdrant (in-memory for now, no cloud needed) ---
client = QdrantClient(":memory:")
client.create_collection(
    collection_name="legal",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)
client.upsert(
    collection_name="legal",
    points=[
        PointStruct(id=i, vector=embeddings[i].tolist(), payload={"text": docs[i]})
        for i in range(len(docs))
    ],
)

# --- 5 & 6. Interactive Q&A Loop ---
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("\nRAG System Ready! Press Ctrl+C to exit.\n")

while True:
    question = input("Ask a question: ").strip()

    if not question:
        continue

    # Embed query
    query_vector = model.encode(question).tolist()

    # Retrieve relevant chunks
    results = client.query_points(
        collection_name="legal",
        query=query_vector,
        limit=2
    ).points

    context = "\n".join(
        [r.payload["text"] for r in results]
    )

    print("\nRetrieved Context:")
    print("-" * 50)
    print(context)
    print("-" * 50)

    # Generate answer
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Answer ONLY from the provided context. If the answer is not present, say 'I don't know based on the provided context.'"
            },
            {
                "role": "user",
                "content": f"""
Context:
{context}


Question:
{question}
"""
            }
        ]
    )

    print("\nAnswer:")
    print(response.choices[0].message.content)
    print("\n" + "=" * 70 + "\n")