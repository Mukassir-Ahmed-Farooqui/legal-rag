# OpenDoc

### AI-Powered Contract Intelligence Platform

OpenDoc is a citation-grounded Legal RAG platform designed for contract analysis, ownership-secured retrieval, and evidence-backed question answering.

<p align="left">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/LangGraph-2C3E50?style=for-the-badge&logo=langchain&logoColor=white" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Qdrant-FF4B4B?style=for-the-badge&logo=qdrant&logoColor=white" alt="Qdrant" />
  <img src="https://img.shields.io/badge/Neon_Postgres-31E88A?style=for-the-badge&logo=postgresql&logoColor=black" alt="Neon Postgres" />
  <img src="https://img.shields.io/badge/JWT_Auth-000000?style=for-the-badge&logo=json-web-tokens&logoColor=white" alt="JWT" />
  <img src="https://img.shields.io/badge/Search-BM25-orange?style=for-the-badge" alt="BM25 Search" />
  <img src="https://img.shields.io/badge/Reranking-RRF-blueviolet?style=for-the-badge" alt="RRF Reranking" />
</p>

---

## 🏗️ System Architecture

The following diagram outlines the system logic flow, from contract ingestion to hybrid retrieval execution:

```mermaid
graph TD
    %% Frontend Ingest
    A[React Frontend] -->|Upload PDF| B[FastAPI Backend]
    A -->|Secure Query| B
    
    %% Ingest Pipeline
    subgraph FastAPI Ingestion Pipeline
        B -->|JWT Verification| C[Authentication Filter]
        C -->|Extract Text & Chunk| D[Smart Chunking Engine]
        D -->|Generate Embeddings| E[Embedding Service]
        E -->|Store Sections & Sentences| F[(Qdrant Vector DB)]
        D -->|Record Contract Metadata| G[(Neon PostgreSQL DB)]
    end
    
    %% Query Pipeline
    subgraph Hybrid Retrieval & Generation
        B -->|Orchestrate workflow| H[LangGraph Coordinator]
        H -->|BM25 Keyword Search| F
        H -->|Dense Vector Search| F
        H -->|Merge Rank Scores| I[Reciprocal Rank Fusion - RRF]
        I -->|Inject Context & Citations| J[LLM Synthesis Engine]
        J -->|Return Citation-Grounded Answer| B
    end

    classDef database fill:#f9f,stroke:#333,stroke-width:2px;
    classDef engine fill:#bbf,stroke:#333,stroke-width:2px;
    class F,G database;
    class D,H,I engine;
```

---

## ✨ Feature Showcase

### 1. Hybrid Retrieval (Dense + BM25 + RRF)
*   **What it does**: Combines dense semantic vector search with keyword-based BM25 sparse search.
*   **Why it matters**: Semantic embeddings capture contextual meaning, but can miss exact codes, section numbers, or acronyms. Sparse search guarantees precision for exact identifiers.
*   **How it was implemented**: Queries are executed in parallel against Qdrant vector spaces and text indices. Results are merged and re-ranked using **Reciprocal Rank Fusion (RRF)** to construct the optimal context window for the LLM.

### 2. Multi-Tenant Ownership Enforcement
*   **What it does**: Ensures that documents, embeddings, and analytics are partitioned strictly per user.
*   **Why it matters**: Enterprise contract management requires rigid isolation. Under no circumstances can User A's queries retrieve context from User B's contracts.
*   **How it was implemented**: Row-level tenant tags are injected into embedding metadata filters within Qdrant and relational queries inside Neon Postgres, checked against signed JWT payload sub claims.

### 3. Citation Grounding & Evidence Snippets
*   **What it does**: Maps LLM generated sentences to verified agreement fragments (source sections, document names, page indices, and text block snippets).
*   **Why it matters**: Prevents hallucination. Legal analysts can click numbered citation chips directly in their query workspace to highlight and preview supporting source text.
*   **How it was implemented**: The LangGraph synthesis step maps retrieval indexes back to source metadata records. Clickable inline components in React use anchor IDs to scroll to and highlight corresponding evidence previews.

---

## 🎬 Reproducible Demonstration Script (2-3 Minutes)

Follow this predefined sequence to demonstrate the capabilities of the OpenDoc platform during reviews or portfolio presentations:

### Scenario 1: User A Contract Analysis & Citations
1.  **Authentication**: Sign in using User A credentials.
2.  **Ingestion**: Drag & drop the `Development Agreement.pdf` contract into the left **Document Repository** panel. Wait for processing to complete.
3.  **Scoped Analysis**:
    *   Select the uploaded `Development Agreement.pdf` contract in the active **Scope Selector** dropdown.
    *   Query: `What are the termination provisions?`
    *   *Inspect*: Verify the "Generated Analysis" card displays the formatted answer in clean Markdown, showing query latency (e.g. `1.8s`) and citation references. Click a citation chip (e.g., `[1]`) to scroll to and highlight the corresponding source section evidence card (e.g. "Section: Term & Termination, Page: 4").
4.  **Evidence Inspection**:
    *   Query: `Who owns the intellectual property created under this agreement?`
    *   *Inspect*: Observe citation highlights referencing intellectual property ownership sections.

### Scenario 2: Corpus-Wide Inferences
5.  **Multi-Contract Querying**:
    *   Set the **Scope Selector** back to `All Contracts (Corpus-wide)`.
    *   Query: `Compare termination provisions across my contracts.`
    *   *Inspect*: Note that OpenDoc synthesizes answers referencing multiple uploaded agreements simultaneously, displaying distinct citations for each source.

### Scenario 3: Ownership Enforcement & Corpus Isolation
6.  **Tenant B Verification**:
    *   Log out from the platform.
    *   Register/Login as **User B**.
    *   *Inspect*: Verify that User B's **Document Repository** list is completely empty. User A's uploaded contracts, vector embeddings, and search inputs are completely hidden and unreachable.
