<div align="center">

# LUNA

**A local-first, memory-augmented AI assistant — fully private, fully yours.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

Luna is a fully **local**, **memory-augmented AI assistant** delivered through a **Chrome Extension**, powered by a custom **FastAPI** backend and **llama.cpp** inference engine. Your data never leaves your machine. Luna learns what you care about, remembers it across sessions, sees what you see in the browser, and can even generate images — all on your own GPU.
</div>

---

## Feature Highlights

| Feature | Description |
|---|---|
| **Split-Brain Memory** | Separate "Working Memory" (auto-pruned) and "Core Memory" (permanent) via ChromaDB. Memory chunks are auto-promoted based on usage frequency. |
| **Advanced RAG Pipeline** | CPU-bound SentenceTransformer embeddings + cross-encoder reranking via FlashRank for high-accuracy context injection into every query. |
| **Multimodal Vision** | Ask Luna about what's on your screen using llm-VL-model. Native visual query support with automatic model hot-swapping. |
| **Local Image Generation** | Automated prompt engineering handed off to a local **ComfyUI** instance via WebSocket tracking — no cloud APIs required. |
| **Thread-Safe Inference** | A custom `llama.cpp` adapter manages VRAM allocation for seamless model hot-swapping (e.g., llm-VL-model ↔ thinking models) without memory fragmentation. |
| **Multimodal Inputs** | Upload images directly into the chat to perform visual analysis, ask questions about photographs, internet search, or use uploaded reference images to guide image generation tasks.
| **DOM Snipping** | Cut any part of a webpage as a image and send it directly to Luna as context via the browser content script. |
| **Autonomous Web Ingestion** | Give Luna a URL and she'll scrape, parse, and memorize the content using Trafilatura for future recall. |
| **Persistent Chat History** | Full conversation history stored locally in SQLite — browse past sessions, search memories, and manage them from the dashboard. |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Chrome Extension (UI)                  │
│   React 18 + TypeScript │ Manifest V3 │ Side Panel      │
│                                                         │
│  ┌──────────────┐  ┌─────────────┐  ┌───────────────┐   │
│  │ ChatInterface│  │ MemoryViewer│  │  SnipperTool  │   │
│  └──────┬───────┘  └──────┬──────┘  └───────┬───────┘   │
│         └─────────────────┼─────────────────┘           │
│                     api.ts (REST)                       │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                       │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  /chat router│  │/memory router│  │  Middleware  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘   │
│         └────────────┬────┘                             │
│                      ▼                                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │                 Core Engines                    │    │
│  │  ┌────────────┐  ┌──────────┐  ┌─────────────┐  │    │
│  │  │ LLM Manager│  │ RAG Core │  │ComfyUI Adptr│  │    │
│  │  │ (llama.cpp)│  │ ChromaDB │  │  WebSocket  │  │    │
│  │  └────────────┘  └──────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────┘    │
│                      ▼                                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Data Layer: SQLite (sessions) + ChromaDB (RAG)  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│           ComfyUI (Optional, port 8188)                 │
│              Local Image Generation                     │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Frontend — Chrome Extension
- **React 18** with TypeScript for the Side Panel UI
- **Webpack 5** with Manifest V3 build system
- **Background Service Workers** for extension lifecycle management
- **Content Scripts** for DOM interaction and snipping
- **CSS Variables** for dynamic theming

### Backend — FastAPI Server
- **Python 3.11+**, FastAPI, Uvicorn (ASGI)
- **SQLAlchemy + aiosqlite** for async SQLite session management
- **Strategy Pattern** adapters for flexible LLM routing (llama.cpp, Ollama, ComfyUI)
- **Alembic** for database migrations

### AI / ML Engine
- **llama-cpp-python** — Local LLM inference on CUDA
- **ChromaDB** — Vector database for dual-tier memory
- **SentenceTransformers** — CPU-bound embedding generation (preserves VRAM for LLM)
- **FlashRank** — Cross-encoder reranking for high-precision retrieval
- **Trafilatura** — Web scraping and article extraction

---

## Directory Structure

```
project-luna/
│
├── extension/                        # Chrome Extension (React + TypeScript)
│   ├── dist/                         # Compiled extension output (load this into Chrome)
│   ├── node_modules/
│   ├── public/                       # Static assets, Manifest V3, HTML entry points
│   ├── src/
│   │   ├── assets/                   # Icons, images, static resources
│   │   ├── background/               # Extension service workers
│   │   │   ├── handlers/
│   │   │   │   └── content-message-handler.ts
│   │   │   └── index.ts
│   │   ├── content/                  # DOM interaction scripts
│   │   │   ├── extractors/
│   │   │   │   └── text-extractor.ts
│   │   │   ├── handlers/
│   │   │   │   └── snipper-handler.ts
│   │   │   └── index.ts
│   │   ├── options/                  # Extension options page
│   │   ├── popup/                    # Extension popup (launcher)
│   │   └── sidebar/                  # Main React UI
│   │       ├── components/
│   │       │   ├── Chat/
│   │       │   │   ├── ChatInterface.tsx       # Main chat window
│   │       │   │   ├── InputBox.tsx            # Message input
│   │       │   │   ├── MessageItem.tsx         # Individual message bubble
│   │       │   │   ├── MessageList.tsx         # Scrollable message feed
│   │       │   │   └── ModelSelector.tsx       # Switch active LLM
│   │       │   └── History/
│   │       │       ├── ConversationHistory.tsx # Conversation History management 
│   │       │       └── MemoryViewer.tsx        # Memory management dashboard
│   │       ├── hooks/
│   │       │   ├── useChat.ts
│   │       │   ├── useHistory.ts
│   │       │   └── useTheme.ts
│   │       ├── styles/
│   │       │   └── sidebar.css
│   │       ├── utils/
│   │       │   └── imageProcessor.ts
│   │       ├── api.ts                # Backend API client
│   │       └── index.tsx             # React entry point
│   ├── declarations.d.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── webpack.config.js
│
└── server/                           # FastAPI Backend
    ├── alembic/                      # Database migration scripts
    ├── models/                       # Local .gguf LLM weight files (not tracked in git)
    ├── rag_data/                     # ChromaDB vector storage & cache (auto-generated)
    ├── src/
    │   ├── agents/                   # Persona definitions
    │   │   ├── registry.py           # Agent registry and routing
    │   │   └── types.py
    │   ├── api/                      # FastAPI app entry & routing
    │   │   ├── routers/
    │   │   │   ├── chat.py           # /chat endpoints
    │   │   │   └── memory.py         # /memory endpoints
    │   │   ├── main.py               # App initialization
    │   │   ├── middleware.py         # CORS, logging, etc.
    │   │   ├── schemas.py            # Pydantic request/response models
    │   │   ├── dependencies.py
    │   │   └── errors.py
    │   ├── config/
    │   │   └── settings.py           # Centralized paths & configuration
    │   ├── core/
    │   │   ├── llm/                  # LLM adapter layer
    │   │   │   ├── base.py           # Abstract LLM interface
    │   │   │   ├── llama_cpp_adapter.py  # llama.cpp integration
    │   │   │   ├── ollama_adapter.py     # Ollama integration
    │   │   │   ├── comfy_adapter.py      # ComfyUI integration
    │   │   │   └── manager.py            # Thread-safe VRAM manager
    │   │   ├── prompts/              # Agent system prompts
    │   │   │   ├── agents/
    │   │   │   │   ├── general.md    # General assistant prompt
    │   │   │   │   ├── creative.md   # Creative writing prompt
    │   │   │   │   └── image_gen.md  # Image generation prompt
    │   │   │   ├── loader.py
    │   │   │   └── manager.py
    │   │   └── rag/                  # Retrieval-Augmented Generation
    │   │       ├── embedder.py       # SentenceTransformer embeddings
    │   │       ├── ingest.py         # Document ingestion pipeline
    │   │       ├── retrieve.py       # Retrieval + FlashRank reranking
    │   │       └── store.py          # ChromaDB working/core memory
    │   ├── data/
    │   │   └── database/
    │   │       ├── __init__.py
    │   │       ├── models.py         # SQLAlchemy ORM models
    │   │       └── sqlite.py         # Async DB session management
    │   └── utils/
    │       └── scraper.py            # Trafilatura web scraping
    ├── tools/
    │   └── comfyui/
    │       └── workflow_api.json     # ComfyUI workflow definition
    ├── luna.db                       # SQLite database (auto-generated)
    ├── pyproject.toml
    ├── poetry.lock
    └── start_luna.bat                # Windows one-click launcher
```

---

## Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Version | Notes |
|---|---|---|
| **Python** | 3.11+ | Required for the backend |
| **Node.js** | 18+ | Required for the extension |
| **npm** | 9+ | Comes with Node.js |
| **Poetry** | Latest | Python dependency management |
| **CUDA GPU** | NVIDIA (CUDA 13.0) | Required for LLM inference |
| **ComfyUI** | Latest | *Optional* — for image generation, runs on port `8188` |

> **VRAM Recommendation**: At least **16 GB VRAM** for running smoothly

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/project-luna.git
cd project-luna
```

### 2. Backend Setup

Navigate to the server directory and install Python dependencies via Poetry.

```bash
cd server
poetry install
```

Open the `server/src/config/settings.py` file to configure your environment and hyperparameters.
Open the `server/src/agents/registry.py` file to configure your models and personas.

Place your `.gguf` model files inside `server/models/`. The system looks for:

| File | Purpose |
|---|---|
| `Qwen3VL-8B-Instruct-Q8_0.gguf` | General - Vision-language model (primary) |
| `mmproj-Qwen3VL-8B-Instruct-F16.gguf` | Vision projector for Qwen-VL |
| `OpenAI-20B-NEOPlus-Uncensored-IQ4_NL.gguf` | Thinking model (optional)|
| `qwen-image-2512-Q4_K_M.gguf` | Image generator model |
| `Qwen_Image-VAE.safetensors` | Variational Autoencoder |
| `Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf` | Image generator decoder |

> 💡 Models are **not included** in this repository due to their size. Download `.gguf` files from [Hugging Face](https://huggingface.co).

Run the database migrations to initialize the SQLite schema:

```bash
poetry run alembic upgrade head
```

### 3. Frontend Setup

Navigate to the extension directory to install dependencies and build the React application.

```bash
cd ../extension
npm install
npm run build
```

This will compile the extension into the `extension/dist/` directory.

---

## Usage

### Starting the Server

```bash
cd server
poetry run python src/api/main.py
```

Or, on **Windows**, use the included batch script:

```bash
start_luna.bat
```

The server will start at **`http://127.0.0.1:8000`**. On first run, it will:
1. Initialize the SQLite database (`luna.db`)
2. Load SentenceTransformer embedding models into CPU memory
3. Initialize ChromaDB collections for Working Memory and Core Memory
4. Stand by for inference requests (models load on first use to save VRAM)

### Loading the Chrome Extension

1. Open Google Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Select the `extension/dist/` folder
5. Pin the Luna extension to your toolbar and click it to open the Side Panel

---

## Memory System Deep Dive

Luna's memory is split into two tiers stored in ChromaDB:

```
┌─────────────────────────────────────────┐
│            Memory Architecture          │
│                                         │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │  Working Memory │  │  Core Memory  │ │
│  │  (Temporary)    │  │  (Permanent)  │ │
│  │                 │  │               │ │
│  │  Auto-pruned    │  │  Persists     │ │
│  │  after TTL      │  │  forever      │ │
│  │                 │  │               │ │
│  │ ──── promote ──►│  │               │ │
│  │  (on high usage)│  │               │ │
│  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────┘
```

- **Working Memory**: Stores temporary context (e.g., content from a current browsing session). Auto-pruned based on a TTL. Frequently accessed chunks are automatically **promoted** to Core Memory.
- **Core Memory**: Stores permanent knowledge — facts, ingested articles, and important context that persists across all sessions.
- **Memory Dashboard**: Accessible from the extension sidebar — view, search, pin, and delete individual memory chunks.

### RAG Retrieval Pipeline

```
Query  ──► SentenceTransformer Embedding (CPU)
       ──► ChromaDB ANN Search (Top-K candidates)
       ──► FlashRank Cross-Encoder Reranking
       ──► Top-N chunks injected into LLM context
```

---

### Visual Analysis & Image Uploads

Luna allows you to interact with images seamlessly using vision-capable models.

**How to use it:**
1. Click the **paperclip icon** next to the chat input bar.
2. Select an image file (JPG, PNG, WEBP) from your computer.
3. A preview thumbnail will appear above the input box.
4. Type your prompt regarding the image (e.g., *"Describe what's in this image"* or *"Extract the text from this screenshot"* or *"Search the internet and find me this image come form"*).
5. Click send.

```text
┌───────────────────────────────────────┐
| ┌─────┐                               |
| |[IMG]| "What type of architecture    |
| └─────┘  is this building?"           |
|                                       |
| [ (/) Attach ] [ Send > ]             |
└───────────────────────────────────────┘
```
---

## Image Generation

Luna integrates with a local [ComfyUI](https://github.com/comfyanonymous/ComfyUI) instance for image generation:

1. Ensure ComfyUI is running locally on port `8188`
2. The `workflow_api.json` in `server/tools/comfyui/` defines the generation workflow
3. Luna auto-engineers prompts using the `image_gen.md` persona before dispatching to ComfyUI
4. Generation progress is tracked in real-time via WebSocket

---

## Available Agent Personas

Luna can switch between different AI personas depending on the task:

| Persona | Prompt File | Best For |
|---|---|---|
| **General** | `general.md` | Everyday questions, research, analysis |
| **Creative** | `creative.md` | Writing, storytelling, brainstorming |
| **Image Gen** | `image_gen.md` | Crafting detailed image generation prompts |

Switch personas using the **Model Selector** component in the sidebar UI.

---

## API Reference

The FastAPI backend exposes the following endpoints under the `/api/v1` prefix (full interactive docs available at `http://127.0.0.1:8000/docs`):

### Chat (`/api/v1/chat`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/` | Send a message and receive a streamed LLM response |
| `GET` | `/sessions` | List all recent conversation sessions |
| `GET` | `/history/{session_id}` | Get full message history for a specific session |
| `DELETE` | `/sessions/{session_id}` | Delete a specific session and its messages |
| `DELETE` | `/sessions` | Wipe all chat history from the database |

### Memory (`/api/v1/memory`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/all` | Retrieve a paginated list of all stored memory chunks |
| `POST` | `/ingest` | Scrape and ingest a URL or raw text into Working Memory |
| `POST` | `/query` | Execute a vector search and FlashRank reranking |
| `DELETE` | `/source` | Delete all memories associated with a specific URL |
| `DELETE` | `/cache` | Flush the short-term retrieval cache |
| `DELETE` | `/wipe` | Nuclear option: Drop all ChromaDB collections |

### System & Image (`/api/v1/image`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/generate` | Unload the LLM and pass a prompt to ComfyUI |

---

## Development

### Running in Development Mode

**Backend (with auto-reload):**
```bash
cd server
poetry run uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend (with watch mode):**
```bash
cd extension
npm run dev
```

### Code Quality

```bash
# Frontend linting
cd extension
npm run lint

# Backend formatting (if configured)
cd server
poetry run ruff check .
poetry run ruff format .
```

---

## Privacy & Security

Luna is designed with **privacy as a core principle**:

- **100% Local** — All inference runs on your machine. No data is sent to external APIs.
- **No Telemetry** — Zero analytics or usage tracking.
- **Local Storage** — Chat history lives in `luna.db` (SQLite) on your disk.
- **Local Vector DB** — Memory chunks are stored in `rag_data/` (ChromaDB) on your disk.
- **Open Weights** — Uses publicly available, open-source GGUF models.

---

## Troubleshooting

**Backend won't start / CUDA errors**
- Ensure `llama-cpp-python` is installed with CUDA support: `CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall`
- Verify your CUDA toolkit version matches your PyTorch/llama.cpp build.

**Extension doesn't load**
- Make sure you ran `npm run build` and are loading the `extension/dist/` folder, not `extension/src/`.
- Check the Chrome Extensions error log for detailed messages.

**Model not found error**
- Confirm `.gguf` files are placed directly in `server/models/` with the exact filenames referenced in your `server/src/config/setting.py` file.

**ComfyUI image generation fails**
- Verify ComfyUI is running on `http://127.0.0.1:8188`.
- Check that the `workflow_api.json` is compatible with your installed ComfyUI nodes.

---

<div align="center">

Made with ☕ and a CUDA GPU &nbsp;|&nbsp; **Project Luna** — *Your AI, your machine, your rules.*

</div>