# AI Browser Assistant - Architecture Documentation

## 1. Chrome Extension Architecture (Detailed)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CHROME EXTENSION LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                    PRESENTATION LAYER                              │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │    │
│  │  │  Sidebar UI     │  │   Popup UI      │  │  Options Page   │  │    │
│  │  │  (React)        │  │   (React)       │  │  (React)        │  │    │
│  │  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤  │    │
│  │  │ - Chat Interface│  │ - Quick Actions │  │ - Settings      │  │    │
│  │  │ - Context Panel │  │ - Status        │  │ - API Config    │  │    │
│  │  │ - History       │  │ - Shortcuts     │  │ - Model Select  │  │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    │ Message Passing                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                    BUSINESS LOGIC LAYER                            │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │         Background Service Worker (Offscreen)            │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐    │    │    │
│  │  │  │        Core Service Orchestrator                │    │    │    │
│  │  │  ├─────────────────────────────────────────────────┤    │    │    │
│  │  │  │ - Request Router                                │    │    │    │
│  │  │  │ - State Manager (Redux/Zustand)                 │    │    │    │
│  │  │  │ - Event Bus                                      │    │    │    │
│  │  │  │ - Session Manager                                │    │    │    │
│  │  │  └─────────────────────────────────────────────────┘    │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │    │
│  │  │  │ AI Agent     │  │ Context      │  │ Tool         │  │    │    │
│  │  │  │ Manager      │  │ Collector    │  │ Executor     │  │    │    │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │    │
│  │  │  │ Memory       │  │ Security     │  │ Analytics    │  │    │    │
│  │  │  │ Store        │  │ Manager      │  │ Tracker      │  │    │    │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │    │
│  │  │                                                            │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    │ chrome.runtime API                     │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                    CONTENT LAYER                                   │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │         Content Scripts (Per Tab/Frame)                  │    │    │
│  │  ├──────────────────────────────────────────────────────────┤    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────┐  ┌─────────────────┐               │    │    │
│  │  │  │ DOM Observer    │  │ Content         │               │    │    │
│  │  │  │ - Mutations     │  │ Extractors      │               │    │    │
│  │  │  │ - Scroll        │  │ - Text          │               │    │    │
│  │  │  │ - Viewport      │  │ - Images        │               │    │    │
│  │  │  └─────────────────┘  │ - Videos        │               │    │    │
│  │  │                        │ - Forms         │               │    │    │
│  │  │                        └─────────────────┘               │    │    │
│  │  │                                                            │    │    │
│  │  │  ┌─────────────────┐  ┌─────────────────┐               │    │    │
│  │  │  │ UI Injector     │  │ Action Handler  │               │    │    │
│  │  │  │ - Highlights    │  │ - Click Events  │               │    │    │
│  │  │  │ - Tooltips      │  │ - Selection     │               │    │    │
│  │  │  │ - Overlays      │  │ - Context Menu  │               │    │    │
│  │  │  └─────────────────┘  └─────────────────┘               │    │    │
│  │  │                                                            │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ WebSocket / HTTP / Native Messaging
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOCAL AI SERVER LAYER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                    API GATEWAY                                     │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │    │
│  │  │ FastAPI      │  │ Auth         │  │ Rate         │           │    │
│  │  │ Server       │  │ Middleware   │  │ Limiter      │           │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │    │
│  │                                                                     │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                AGENT ORCHESTRATION LAYER                           │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                   (See detailed AI Architecture below)                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Vector DB    │  │ SQLite       │  │ Redis        │  │ File Storage │  │
│  │ (ChromaDB)   │  │ (Metadata)   │  │ (Cache)      │  │ (Models)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Communication Flow

```
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│ Content  │ ──────► │ Background   │ ──────► │ Local AI     │
│ Script   │ Message │ Service      │  HTTP   │ Server       │
└──────────┘         └──────────────┘         └──────────────┘
     │                      │                         │
     │                      │                         │
     ▼                      ▼                         ▼
┌──────────┐         ┌──────────────┐         ┌──────────────┐
│ User     │         │ State Store  │         │ Vector DB    │
│ Interface│◄────────│ (Extension)  │◄────────│ (Embeddings) │
└──────────┘         └──────────────┘         └──────────────┘
```

## 3. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Extension Permissions (Manifest V3)              │
│  ├─ activeTab (user-initiated only)                        │
│  ├─ storage (encrypted local storage)                      │
│  ├─ contextMenus (user actions)                            │
│  └─ host_permissions (explicit domains)                    │
│                                                             │
│  Layer 2: Content Security Policy                          │
│  ├─- No eval()                                             │
│  ├─ Strict CSP headers                                     │
│  └─ HTTPS-only connections                                 │
│                                                             │
│  Layer 3: API Authentication                               │
│  ├─ JWT tokens (short-lived)                               │
│  ├─ API key rotation                                       │
│  └─ Localhost binding (127.0.0.1)                          │
│                                                             │
│  Layer 4: Data Protection                                  │
│  ├─ Encryption at rest (AES-256)                           │
│  ├─ Memory isolation                                       │
│  └─ Sanitization (DOMPurify)                               │
│                                                             │
│  Layer 5: Privacy Controls                                 │
│  ├─ No external data transmission                          │
│  ├─ User consent for data collection                       │
│  └─ Data retention policies                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 4. Performance Optimization

```
┌─────────────────────────────────────────────────────────────┐
│              PERFORMANCE OPTIMIZATION STRATEGY              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend (Extension)                                       │
│  ├─ Code Splitting (React.lazy)                            │
│  ├─ Web Workers (heavy computations)                       │
│  ├─ Virtual Scrolling (large lists)                        │
│  ├─ Debouncing/Throttling (user inputs)                    │
│  └─ IndexedDB (large data storage)                         │
│                                                             │
│  Backend (AI Server)                                        │
│  ├─ Model Quantization (INT8/INT4)                         │
│  ├─ Batch Processing (multiple requests)                   │
│  ├─ Response Streaming (SSE)                               │
│  ├─ Connection Pooling                                     │
│  └─ Request Queue (priority-based)                         │
│                                                             │
│  Caching Strategy                                           │
│  ├─ L1: Browser Memory (hot data)                          │
│  ├─ L2: IndexedDB (warm data)                              │
│  ├─ L3: Redis (server cache)                               │
│  └─ L4: Vector DB (embeddings)                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 5. Data Flow Diagram

```
User Action
    │
    ▼
┌────────────────┐
│ Content Script │
│ (Inject)       │
└────────────────┘
    │
    │ chrome.runtime.sendMessage()
    ▼
┌────────────────────────┐
│ Background Service     │
│ ┌────────────────────┐ │
│ │ 1. Validate        │ │
│ │ 2. Enrich Context  │ │
│ │ 3. Route to Agent  │ │
│ └────────────────────┘ │
└────────────────────────┘
    │
    │ HTTP POST
    ▼
┌────────────────────────┐
│ Local AI Server        │
│ ┌────────────────────┐ │
│ │ 1. Auth Check      │ │
│ │ 2. Agent Selection │ │
│ │ 3. Tool Execution  │ │
│ │ 4. Response Gen    │ │
│ └────────────────────┘ │
└────────────────────────┘
    │
    │ SSE Stream / JSON
    ▼
┌────────────────────────┐
│ Background Service     │
│ (Update State)         │
└────────────────────────┘
    │
    │ chrome.runtime.sendMessage()
    ▼
┌────────────────┐
│ UI Component   │
│ (Render)       │
└────────────────┘
```

## 6. Extension Lifecycle

```
Installation
    │
    ▼
┌────────────────┐
│ onInstalled    │
│ - Setup DB     │
│ - Init Config  │
│ - Show Welcome │
└────────────────┘
    │
    ▼
┌────────────────┐
│ Runtime        │
│ - Listen Events│
│ - Maintain     │
│   Connection   │
└────────────────┘
    │
    ▼
┌────────────────┐
│ Update/Reload  │
│ - Migrate Data │
│ - Reconnect    │
│ - Notify User  │
└────────────────┘
```
