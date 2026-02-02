# Local AI Architecture - Detailed Documentation

## 1. Overall AI System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LOCAL AI SERVER (FastAPI + Python 3.11)                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                    API GATEWAY LAYER                              │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │    │
│  │  │ REST API     │  │ WebSocket    │  │ SSE          │           │    │
│  │  │ Endpoints    │  │ Handler      │  │ Streaming    │           │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │    │
│  │         │                  │                  │                   │    │
│  │         └──────────────────┴──────────────────┘                   │    │
│  │                            │                                       │    │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │
│  │  │            Middleware Stack                              │   │    │
│  │  ├──────────────────────────────────────────────────────────┤   │    │
│  │  │ Authentication │ Rate Limiting │ CORS │ Logging          │   │    │
│  │  └──────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                  ORCHESTRATION LAYER                               │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │            Master Orchestrator                           │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │                                                            │    │    │
│  │  │  • Request Router & Parser                               │    │    │
│  │  │  • Intent Classification (ML-based)                      │    │    │
│  │  │  • Agent Selection & Dispatch                            │    │    │
│  │  │  • Response Aggregator                                   │    │    │
│  │  │  • Error Handler & Recovery                              │    │    │
│  │  │                                                            │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                     AGENT LAYER                                    │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │    │
│  │  │ Research    │  │ Content     │  │ Automation  │              │    │
│  │  │ Agent       │  │ Agent       │  │ Agent       │              │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │    │
│  │                                                                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │    │
│  │  │ Analysis    │  │ Coding      │  │ Summarizer  │              │    │
│  │  │ Agent       │  │ Agent       │  │ Agent       │              │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │    │
│  │                                                                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │    │
│  │  │ Vision      │  │ Memory      │  │ Coordinator │              │    │
│  │  │ Agent       │  │ Agent       │  │ Agent       │              │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                      CORE LAYER                                    │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Language Model Manager                      │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │         Model Registry                          │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • LLaMA 3.1 (8B, 70B)                           │    │    │    │
│  │  │  │ • Mistral (7B, Mixtral 8x7B)                    │    │    │    │
│  │  │  │ • Qwen 2.5 (7B, 14B, 32B)                       │    │    │    │
│  │  │  │ • Phi-3 (Mini, Medium)                          │    │    │    │
│  │  │  │ • Code-specific (CodeLlama, DeepSeek)           │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │         Model Adapter (Unified Interface)       │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Ollama API                                    │    │    │    │
│  │  │  │ • llama.cpp                                     │    │    │    │
│  │  │  │ • vLLM                                          │    │    │    │
│  │  │  │ • HuggingFace Transformers                      │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │         Inference Engine                        │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Quantization (INT8, INT4, GPTQ, AWQ)          │    │    │    │
│  │  │  │ • Batching & Caching                            │    │    │    │
│  │  │  │ • KV Cache Management                           │    │    │    │
│  │  │  │ • Flash Attention 2                             │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Prompt Engineering System                   │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │ • Template Manager (Jinja2)                              │    │    │
│  │  │ • Dynamic Prompt Construction                            │    │    │
│  │  │ • Chain-of-Thought Injection                             │    │    │
│  │  │ • Few-shot Learning Examples                             │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Context Management                          │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │ • Token Counter & Optimizer                              │    │    │
│  │  │ • Context Window Manager (128K tokens)                   │    │    │
│  │  │ • Conversation History Compression                       │    │    │
│  │  │ • Sliding Window (for long contexts)                     │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                    TOOLS LAYER                                     │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Tool Registry & Executor                    │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │                                                            │    │    │
│  │  │  Web Tools:                                               │    │    │
│  │  │  ├─ Web Scraper (BeautifulSoup, Playwright)              │    │    │
│  │  │  ├─ Search Engine Interface (DuckDuckGo, Searxng)        │    │    │
│  │  │  ├─ URL Analyzer                                          │    │    │
│  │  │  └─ DOM Manipulator                                       │    │    │
│  │  │                                                            │    │    │
│  │  │  Vision Tools:                                            │    │    │
│  │  │  ├─ Image OCR (PaddleOCR, Tesseract)                     │    │    │
│  │  │  ├─ Object Detection (YOLO, DETR)                        │    │    │
│  │  │  ├─ Image Classification (CLIP, DINOv2)                  │    │    │
│  │  │  ├─ Screenshot Analyzer                                   │    │    │
│  │  │  └─ Video Frame Extractor                                │    │    │
│  │  │                                                            │    │    │
│  │  │  Code Tools:                                              │    │    │
│  │  │  ├─ Code Executor (Sandboxed Python/JS)                  │    │    │
│  │  │  ├─ Syntax Validator                                      │    │    │
│  │  │  ├─ Code Formatter (Black, Prettier)                     │    │    │
│  │  │  └─ AST Parser                                            │    │    │
│  │  │                                                            │    │    │
│  │  │  Data Tools:                                              │    │    │
│  │  │  ├─ File I/O (CSV, JSON, XML)                            │    │    │
│  │  │  ├─ Database Query (SQL)                                 │    │    │
│  │  │  ├─ Data Transformer (Pandas)                            │    │    │
│  │  │  └─ Calculator (NumPy)                                    │    │    │
│  │  │                                                            │    │    │
│  │  │  Browser Tools:                                           │    │    │
│  │  │  ├─ Tab Manager                                           │    │    │
│  │  │  ├─ Bookmark Organizer                                    │    │    │
│  │  │  ├─ History Analyzer                                      │    │    │
│  │  │  └─ Form Filler                                           │    │    │
│  │  │                                                            │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Tool Validation & Security                  │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │ • Input Sanitization                                      │    │    │
│  │  │ • Execution Timeout                                       │    │    │
│  │  │ • Resource Limits (CPU, Memory)                          │    │    │
│  │  │ • Sandboxing (Docker, firejail)                          │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                  RAG (Retrieval-Augmented Generation) LAYER        │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Embedding Pipeline                          │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │     Embedding Models                            │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • sentence-transformers/all-MiniLM-L6-v2        │    │    │    │
│  │  │  │ • BAAI/bge-large-en-v1.5                        │    │    │    │
│  │  │  │ • intfloat/e5-large-v2                          │    │    │    │
│  │  │  │ • OpenAI-compatible endpoints                   │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │     Document Processing                         │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Text Splitter (Recursive, Semantic)           │    │    │    │
│  │  │  │ • Metadata Extractor                            │    │    │    │
│  │  │  │ • Multi-format Parser (PDF, DOCX, HTML)         │    │    │    │
│  │  │  │ • Deduplication                                 │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Vector Store (ChromaDB)                     │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │                                                            │    │    │
│  │  │  Collections:                                             │    │    │
│  │  │  ├─ browsing_history                                      │    │    │
│  │  │  ├─ bookmarks                                             │    │    │
│  │  │  ├─ web_content                                           │    │    │
│  │  │  ├─ user_documents                                        │    │    │
│  │  │  ├─ conversation_history                                  │    │    │
│  │  │  └─ knowledge_base                                        │    │    │
│  │  │                                                            │    │    │
│  │  │  Indexing:                                                │    │    │
│  │  │  ├─ HNSW (Hierarchical Navigable Small World)            │    │    │
│  │  │  ├─ Distance Metrics (Cosine, L2, IP)                    │    │    │
│  │  │  └─ Hybrid Search (Dense + Sparse)                       │    │    │
│  │  │                                                            │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Retrieval Strategy                          │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │     Query Processing                            │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Query Expansion (synonyms, related terms)     │    │    │    │
│  │  │  │ • Query Rewriting (clarification)               │    │    │    │
│  │  │  │ • Multi-query Generation                        │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │     Retrieval Methods                           │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Dense Retrieval (Vector Similarity)           │    │    │    │
│  │  │  │ • Sparse Retrieval (BM25, TF-IDF)               │    │    │    │
│  │  │  │ • Hybrid (Ensemble)                             │    │    │    │
│  │  │  │ • Re-ranking (Cross-encoder)                    │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │     Context Augmentation                        │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Relevance Filtering (threshold-based)         │    │    │    │
│  │  │  │ • Diversity Sampling (MMR)                      │    │    │    │
│  │  │  │ • Contextual Compression                        │    │    │    │
│  │  │  │ • Source Attribution                            │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                  GOVERNANCE & SAFETY LAYER                         │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Content Moderation                          │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │ • Input Validation (PII detection, toxic content)        │    │    │
│  │  │ • Output Filtering (harmful content)                     │    │    │
│  │  │ • Guardrails (NeMo, Llama Guard)                         │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Privacy & Compliance                        │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │ • Data Anonymization                                      │    │    │
│  │  │ • Access Control (RBAC)                                   │    │    │
│  │  │ • Audit Logging                                           │    │    │
│  │  │ • GDPR Compliance (data deletion, export)                │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Resource Management                         │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │ • Rate Limiting (per user, per endpoint)                 │    │    │
│  │  │ • Quota Management                                        │    │    │
│  │  │ • Cost Tracking (token usage, GPU time)                  │    │    │
│  │  │ • Priority Queue                                          │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Monitoring & Observability                  │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │ • Metrics (Prometheus)                                    │    │    │
│  │  │ • Logging (Structured JSON)                              │    │    │
│  │  │ • Tracing (OpenTelemetry)                                │    │    │
│  │  │ • Alerting (threshold-based)                             │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                  AGENT HANDOFF & COORDINATION LAYER                │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              Handoff Coordinator                         │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │     Task Decomposition                          │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Break complex tasks into subtasks             │    │    │    │
│  │  │  │ • Dependency graph construction                 │    │    │    │
│  │  │  │ • Parallel execution planning                   │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │     Agent Selection Strategy                    │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Capability matching                           │    │    │    │
│  │  │  │ • Load balancing                                │    │    │    │
│  │  │  │ • Specialization routing                        │    │    │    │
│  │  │  │ • Fallback mechanisms                           │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │     Inter-Agent Communication                   │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Message Queue (Redis Pub/Sub)                 │    │    │    │
│  │  │  │ • Shared Memory (Context passing)               │    │    │    │
│  │  │  │ • Event Broadcasting                            │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │     Workflow Execution                          │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ • Sequential chains                             │    │    │    │
│  │  │  │ • Parallel branches                             │    │    │    │
│  │  │  │ • Conditional routing                           │    │    │    │
│  │  │  │ • Loop & retry logic                            │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │              State Management                            │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │ • Session Store (conversation state)                     │    │    │
│  │  │ • Task Progress Tracking                                 │    │    │
│  │  │ • Checkpoint & Resume                                    │    │    │
│  │  │ • Rollback Capability                                    │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Agent Architecture Deep Dive

```
┌──────────────────────────────────────────────────────────┐
│                  INDIVIDUAL AGENT STRUCTURE              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │          Agent Core                            │    │
│  ├────────────────────────────────────────────────┤    │
│  │                                                 │    │
│  │  class BaseAgent:                              │    │
│  │      - name: str                               │    │
│  │      - description: str                        │    │
│  │      - capabilities: List[str]                 │    │
│  │      - model: LanguageModel                    │    │
│  │      - tools: List[Tool]                       │    │
│  │      - memory: Memory                          │    │
│  │      - system_prompt: str                      │    │
│  │                                                 │    │
│  │      Methods:                                  │    │
│  │      - process(input) -> output                │    │
│  │      - plan(task) -> steps                     │    │
│  │      - execute(step) -> result                 │    │
│  │      - reflect(result) -> insights             │    │
│  │                                                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │          Agent Types                           │    │
│  ├────────────────────────────────────────────────┤    │
│  │                                                 │    │
│  │  1. Research Agent                             │    │
│  │     - Web search & analysis                    │    │
│  │     - Multi-source aggregation                 │    │
│  │     - Fact verification                        │    │
│  │     Tools: [WebSearch, URLFetch, PDFReader]    │    │
│  │                                                 │    │
│  │  2. Content Agent                              │    │
│  │     - Text extraction & summarization          │    │
│  │     - Translation                              │    │
│  │     - Content generation                       │    │
│  │     Tools: [TextExtractor, Translator]         │    │
│  │                                                 │    │
│  │  3. Vision Agent                               │    │
│  │     - Image analysis                           │    │
│  │     - OCR                                       │    │
│  │     - Object detection                         │    │
│  │     Tools: [OCR, ObjectDetector, ImageCap]     │    │
│  │                                                 │    │
│  │  4. Automation Agent                           │    │
│  │     - Form filling                             │    │
│  │     - Multi-step workflows                     │    │
│  │     - Browser control                          │    │
│  │     Tools: [FormFiller, TabManager]            │    │
│  │                                                 │    │
│  │  5. Coding Agent                               │    │
│  │     - Code generation & review                 │    │
│  │     - Debugging assistance                     │    │
│  │     - Documentation                            │    │
│  │     Tools: [CodeExecutor, Linter]              │    │
│  │                                                 │    │
│  │  6. Coordinator Agent (Meta-agent)             │    │
│  │     - Task delegation                          │    │
│  │     - Agent orchestration                      │    │
│  │     - Conflict resolution                      │    │
│  │     Tools: [AgentRegistry, TaskQueue]          │    │
│  │                                                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## 3. RAG Pipeline Detailed Flow

```
User Query: "What did I read about AI yesterday?"
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Step 1: Query Analysis                                 │
├────────────────────────────────────────────────────────┤
│ • Extract entities: ["AI", "yesterday"]                │
│ • Intent: retrieve_history                             │
│ • Temporal filter: date = yesterday                    │
│ • Expected source: browsing_history                    │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Query Expansion                                │
├────────────────────────────────────────────────────────┤
│ Original: "AI"                                         │
│ Expanded: ["AI", "artificial intelligence",           │
│            "machine learning", "neural networks"]      │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Step 3: Embedding Generation                           │
├────────────────────────────────────────────────────────┤
│ Model: bge-large-en-v1.5                               │
│ Query Embedding: [0.234, -0.123, 0.456, ...]          │
│ Dimension: 1024                                        │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Vector Search                                  │
├────────────────────────────────────────────────────────┤
│ Collection: browsing_history                           │
│ Method: HNSW + Cosine Similarity                       │
│ Filters: metadata.timestamp = yesterday                │
│ Top-K: 20 documents                                    │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Step 5: Re-ranking                                     │
├────────────────────────────────────────────────────────┤
│ Model: cross-encoder/ms-marco-MiniLM-L-6-v2            │
│ Score each document against original query             │
│ Select Top-5 after re-ranking                          │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Step 6: Context Construction                           │
├────────────────────────────────────────────────────────┤
│ • Add source metadata                                  │
│ • Format: "Source: [URL] | Content: [text]"           │
│ • Total tokens: ~2000 (within context limit)           │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Step 7: Prompt Construction                            │
├────────────────────────────────────────────────────────┤
│ Template:                                              │
│ """                                                    │
│ Context from your browsing history:                    │
│ {retrieved_documents}                                  │
│                                                        │
│ Question: {user_query}                                 │
│                                                        │
│ Answer based on the context, citing sources.           │
│ """                                                    │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Step 8: LLM Generation                                 │
├────────────────────────────────────────────────────────┤
│ Model: Qwen 2.5 14B                                    │
│ Temperature: 0.3 (factual)                             │
│ Max Tokens: 500                                        │
│ Output: Formatted answer with citations                │
└────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────┐
│ Step 9: Response Post-processing                       │
├────────────────────────────────────────────────────────┤
│ • Validate citations                                   │
│ • Add metadata (sources, confidence)                   │
│ • Format for display                                   │
└────────────────────────────────────────────────────────┘
    │
    ▼
Final Answer to User
```

## 4. Memory Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  MEMORY SYSTEM                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Short-term Memory (Working Memory)                     │
│  ┌────────────────────────────────────────────────┐    │
│  │ • Current conversation context                 │    │
│  │ • Recent tool outputs                          │    │
│  │ • Active task state                            │    │
│  │ Storage: Redis (TTL: 1 hour)                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Long-term Memory (Episodic)                            │
│  ┌────────────────────────────────────────────────┐    │
│  │ • Conversation history (summarized)            │    │
│  │ • User preferences & patterns                  │    │
│  │ • Learned facts about user                     │    │
│  │ Storage: Vector DB + SQLite                    │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Semantic Memory (Knowledge)                            │
│  ┌────────────────────────────────────────────────┐    │
│  │ • Extracted web content                        │    │
│  │ • Bookmarks & annotations                      │    │
│  │ • Documents & files                            │    │
│  │ Storage: Vector DB (persistent)                │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Procedural Memory (Skills)                             │
│  ┌────────────────────────────────────────────────┐    │
│  │ • Tool usage patterns                          │    │
│  │ • Successful strategies                        │    │
│  │ • Error recovery methods                       │    │
│  │ Storage: Config files + DB                     │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## 5. Tool Execution Flow

```
Agent requests tool execution
    │
    ▼
┌────────────────────────────────┐
│ Tool Execution Framework       │
├────────────────────────────────┤
│ 1. Validate permissions        │
│ 2. Check resource limits       │
│ 3. Prepare sandbox             │
│ 4. Execute with timeout        │
│ 5. Capture output/errors       │
│ 6. Cleanup resources           │
│ 7. Return structured result    │
└────────────────────────────────┘
    │
    ▼
Result returned to Agent
    │
    ▼
Agent processes result
    │
    ├─ Success → Continue
    └─ Failure → Retry or fallback
```
