import base64
import requests

mermaid_code = """flowchart TD
  subgraph BlueprintContainer ["<b>SYSTEMS ENGINEERING BLUEPRINT</b>"]
    %% Title
    TitleNode["LEGAL RAG SYSTEM WORKFLOW"]
    style TitleNode fill:none,stroke:none,color:#ffffff,font-size:24px,font-weight:bold;

    %% Left Track - Ingestion
    subgraph IngestionGroup ["<b>CONTRACT INGESTION PIPELINE</b>"]
      Upload("📄 <b>UPLOAD CONTRACT</b><br/>(PDF / TXT)"):::user
      Loader("📥 <b>DOCUMENT LOADER</b><br/>(Read Files)"):::proc
      Extraction("⚙️ <b>TEXT EXTRACTION</b><br/>(Docling Engine)"):::proc
      Chunking("🧩 <b>SMART CHUNKING</b><br/>(Sections & Sentences)"):::proc
      Embedding("🔢 <b>EMBEDDING GEN</b><br/>(Local BGE Model)"):::proc
      Qdrant[("🛢️ <b>QDRANT STORAGE</b><br/>(Vector Collections)")]:::db
    end

    %% Right Track - Query
    subgraph QueryGroup ["<b>HYBRID QUERY & GENERATION FLOW</b>"]
      Question("💬 <b>USER QUESTION</b><br/>(Query Input)"):::user
      DocSpecific{"🔍 <b>DOCUMENT-SPECIFIC?</b>"}:::deci
      FilteredSearch("🎯 <b>FILTERED SEARCH</b><br/>(Filter by Doc UUID)"):::retr
      GlobalSearch("🌐 <b>GLOBAL SEARCH</b><br/>(Search All Docs)"):::retr
      Retrieval("🔍 <b>HYBRID RETRIEVAL</b><br/>(Dense + BM25)"):::retr
      Fusion("🔀 <b>RRF FUSION</b><br/>(Reciprocal Rank)"):::retr
      TopContext("📋 <b>TOP CONTEXT SELECTION</b><br/>(Structured Context)"):::retr
      LLM("🤖 <b>LLM REASONING</b><br/>(Groq Llama-3)"):::gen
      Citations("📌 <b>CITATION GENERATION</b><br/>(Clause & Page Refs)"):::gen
      Answer("💡 <b>FINAL LEGAL ANSWER</b><br/>(With Citations)"):::gen
    end

    %% Legend
    subgraph LegendGroup ["<b>SYSTEM LEGEND</b>"]
      L_User(["🔵 User Interaction"]):::user
      L_Proc(["🟣 Document Processing"]):::proc
      L_Retr(["🟠 Retrieval Pipeline"]):::retr
      L_Gen(["🟢 LLM & Answer Gen"]):::gen
      L_Deci{"🔴 Decision Node"}:::deci
      L_Db[("🔵 Database Collection")]:::db
    end

    %% Ingestion Path
    Upload ==> Loader
    Loader ==> Extraction
    Extraction ==> Chunking
    Chunking ==> Embedding
    Embedding ==> Qdrant

    %% Query Path
    Question ==> DocSpecific
    DocSpecific ==>|Yes| FilteredSearch
    DocSpecific ==>|No| GlobalSearch
    FilteredSearch ==> Retrieval
    GlobalSearch ==> Retrieval
    Qdrant ==>|Index Reference| Retrieval
    Retrieval ==> Fusion
    Fusion ==> TopContext
    TopContext ==> LLM
    LLM ==> Citations
    Citations ==> Answer

    %% Stylings for subgraphs
    style IngestionGroup fill:#0a1128,stroke:#8b5cf6,stroke-width:2px,stroke-dasharray: 5 5,color:#ffffff;
    style QueryGroup fill:#0a1128,stroke:#3b82f6,stroke-width:2px,stroke-dasharray: 5 5,color:#ffffff;
    style LegendGroup fill:#0a1128,stroke:#64748b,stroke-width:2px,color:#ffffff;
  end

  style BlueprintContainer fill:#050914,stroke:#1e293b,stroke-width:4px,color:#ffffff;

  %% Vibrant Presentation Colors (Neon Glowing theme on Navy Background)
  classDef user fill:#1e3a8a,stroke:#3b82f6,stroke-width:3px,color:#ffffff,font-size:14px;
  classDef proc fill:#4c1d95,stroke:#8b5cf6,stroke-width:3px,color:#ffffff,font-size:14px;
  classDef retr fill:#7c2d12,stroke:#ea580c,stroke-width:3px,color:#ffffff,font-size:14px;
  classDef gen fill:#064e3b,stroke:#10b981,stroke-width:3px,color:#ffffff,font-size:14px;
  classDef deci fill:#7f1d1d,stroke:#ef4444,stroke-width:3px,color:#ffffff,font-size:14px;
  classDef db fill:#164e63,stroke:#06b6d4,stroke-width:3px,color:#ffffff,font-size:14px;

  %% Link default styling
  linkStyle default stroke:#94a3b8,stroke-width:3px;"""

# Encode using URL-safe base64
encoded_b64 = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8').rstrip("=")

# Construct the correct URL: /img/<base64>?type=png
url = f"https://mermaid.ink/img/{encoded_b64}?type=png"

print(f"Requesting URL: {url[:100]}...")
response = requests.get(url)

if response.status_code == 200:
    output_path = "system_architecture.png"
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"Successfully saved diagram to {output_path}")
else:
    print(f"Error {response.status_code}: {response.text}")
