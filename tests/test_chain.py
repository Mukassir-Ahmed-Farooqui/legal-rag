from src.chain import LegalRAG

rag = LegalRAG()

result = rag.ask(
    "What transfer restrictions apply?"
)

print("\n=== ANSWER ===\n")
print(result["answer"])

print("\n=== SOURCES ===\n")

for i, c in enumerate(
    result["citations"],
    start=1,
):
    print(
        f"[{i}] "
        f"{c['document']} "
        f"— Page {c['page']} "
        f"— {c['section']}"
    )