# 📝 Phase 3: The "Split-Brain" RAG System

**Objective:** Give Luna long-term memory and web-reading capabilities without crashing the GPU (0GB VRAM usage for RAG).
**Strategy:** CPU-Based Embeddings/Reranking + Automated Tiered Memory.

---

## 🛠️ Phase 3.1: Foundation & Dependencies (The Setup)
- [ ] **Install Core Libraries**
    - `chromadb` (Vector Store - Runs on Disk/RAM)
    - `diskcache` (Semantic Cache - Runs on Disk)
    - `sentence-transformers` (Embeddings - CPU Optimized)
    - `flashrank` (Reranking - CPU Optimized)
    - `beautifulsoup4` (HTML Cleaning)
- [ ] **Create Folder Structure**
    - `server/src/core/rag/`
        - `__init__.py`
        - `settings.py` (RAG-specific configs)
        - `embedder.py` (CPU Wrapper)
        - `store.py` (Chroma + SQLite Manager)
        - `ingest.py` (The Gatekeeper / Hasher)
        - `retrieve.py` (The Brain / Automation)

---

## 🧠 Phase 3.2: The "Split-Brain" Engine (CPU Logic)
- [ ] **Implement CPU Embedder (`embedder.py`)**
    - Load `all-MiniLM-L6-v2` on **CPU only**.
    - Ensure strict "No GPU" flags are set.
- [ ] **Implement CPU Reranker**
    - Initialize `FlashRank` (TinyBERT).
    - Create a helper function `rerank_documents(query, docs) -> top_k`.

---

## 🗄️ Phase 3.3: The Data Layer (The Memory)
- [ ] **Initialize Database (`store.py`)**
    - Setup **ChromaDB** Persistent Client.
    - Create Two Collections:
        - `working_memory` (Metadata: `{"retention": "5_days"}`)
        - `core_memory` (Metadata: `{"retention": "forever"}`)
- [ ] **Initialize Metadata Store (SQLite)**
    - Create `memory_stats` table:
        - `id` (PK), `url` (Unique), `usage_count`, `created_at`, `last_accessed`, `tier` ("temp"/"core").
- [ ] **Initialize Cache (DiskCache)**
    - Setup a simple key-value store for exact Q&A matching.

---

## 🛡️ Phase 3.4: The Ingestion Pipeline (The Gatekeeper)
- [ ] **Implement Deduplication Logic (`ingest.py`)**
    - Create `generate_deterministic_id(url, chunk_index)` function.
    - **Logic:** `Hash(url) + "_" + index`.
- [ ] **Implement "Upsert" Workflow**
    - Check SQLite: * "Do we have this URL?"*
    - If **Yes**: Delete old chunks from Chroma (Update Mode).
    - If **No**: Insert new chunks.
- [ ] **Implement Text Splitting**
    - Recursive Character Splitter (Chunk Size: ~500 words).
    - Attach Metadata: `{ "source": url, "tier": "temp" }`.

---

## 🌪️ Phase 3.5: The Retrieval Pipeline (The Flow)
- [ ] **Implement Search Logic (`retrieve.py`)**
    - **Step 1:** Check `DiskCache`. (Hit? Return instantly).
    - **Step 2:** Search **Core Memory** (Vault).
    - **Step 3:** Search **Working Memory** (Scratchpad).
    - **Step 4:** Rerank combined results (FlashRank).
    - **Step 5:** Return Top 3 Chunks.
- [ ] **Implement Automation ("Rule of 5")**
    - **Update Stats:** Increment `usage_count` in SQLite for retrieved chunks.
    - **Promotion Check:** If `usage_count >= 5` AND `tier == 'temp'`:
        - Move data from `working_memory` -> `core_memory`.
        - Update SQLite tier to `core`.
- [ ] **Implement Cleanup Task**
    - On Startup: Delete rows from SQLite & Chroma where `tier == 'temp'` AND `age > 5 days`.

---

## 🔌 Phase 3.6: Integration
- [ ] **Create API Endpoints (`server/src/api/routers/memory.py`)**
    - `POST /ingest` (Input: URL/Text)
    - `POST /query` (Input: Question) -> Returns context for LLM.
- [ ] **Connect to Chat Loop**
    - Update `chat.py` to call `memory.query` before sending prompt to LLM.

---

## ✅ Final Verification (The "Crash Test")
- [ ] **VRAM Check:** Run `nvidia-smi` while RAG is searching. (Must remain at 0% change).
- [ ] **Duplicate Check:** Scan the same URL 3 times. Verify only 1 set of chunks exists in DB.
- [ ] **Promotion Check:** Ask about a topic 5 times. Verify it moves to "Core" collection.