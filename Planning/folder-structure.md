# AI Browser Assistant - Enterprise Production-Grade Folder Structure

```
ai-browser-assistant/
│
├── 📁 .github/                              # GitHub configuration
│   ├── workflows/                           # CI/CD pipelines
│   │   ├── extension-build.yml              # Extension build & test
│   │   ├── server-test.yml                  # Backend tests
│   │   ├── e2e-tests.yml                    # End-to-end tests
│   │   ├── security-scan.yml                # Security scanning
│   │   └── release.yml                      # Release automation
│   ├── ISSUE_TEMPLATE/                      # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md             # PR template
│   └── dependabot.yml                       # Dependency updates
│
├── 📁 docs/                                 # Documentation
│   ├── architecture/                        # Architecture docs
│   │   ├── system-design.md
│   │   ├── agent-architecture.md
│   │   ├── rag-pipeline.md
│   │   └── security-model.md
│   ├── api/                                 # API documentation
│   │   ├── extension-api.md
│   │   ├── server-api.md
│   │   └── openapi.yaml
│   ├── guides/                              # User & developer guides
│   │   ├── installation.md
│   │   ├── configuration.md
│   │   ├── development.md
│   │   └── deployment.md
│   ├── ADR/                                 # Architecture Decision Records
│   │   ├── 001-technology-stack.md
│   │   ├── 002-agent-framework.md
│   │   └── 003-rag-strategy.md
│   └── assets/                              # Images, diagrams
│
├── 📁 extension/                            # Chrome Extension (Frontend)
│   ├── src/
│   │   ├── background/                      # Background service worker
│   │   │   ├── index.ts                     # Entry point
│   │   │   ├── services/                    # Background services
│   │   │   │   ├── ai-agent-manager.ts
│   │   │   │   ├── context-collector.ts
│   │   │   │   ├── tool-executor.ts
│   │   │   │   ├── memory-store.ts
│   │   │   │   ├── security-manager.ts
│   │   │   │   └── analytics-tracker.ts
│   │   │   ├── handlers/                    # Message handlers
│   │   │   │   ├── content-message-handler.ts
│   │   │   │   ├── popup-message-handler.ts
│   │   │   │   └── sidebar-message-handler.ts
│   │   │   ├── state/                       # State management
│   │   │   │   ├── store.ts                 # Redux/Zustand store
│   │   │   │   ├── slices/
│   │   │   │   │   ├── conversation.slice.ts
│   │   │   │   │   ├── settings.slice.ts
│   │   │   │   │   └── session.slice.ts
│   │   │   │   └── middleware/
│   │   │   │       ├── logger.middleware.ts
│   │   │   │       └── persistence.middleware.ts
│   │   │   ├── api/                         # API clients
│   │   │   │   ├── local-ai-client.ts
│   │   │   │   ├── websocket-client.ts
│   │   │   │   └── http-client.ts
│   │   │   └── utils/
│   │   │       ├── message-router.ts
│   │   │       ├── error-handler.ts
│   │   │       └── retry-logic.ts
│   │   │
│   │   ├── content/                         # Content scripts
│   │   │   ├── index.ts                     # Entry point
│   │   │   ├── observers/                   # DOM observers
│   │   │   │   ├── mutation-observer.ts
│   │   │   │   ├── scroll-observer.ts
│   │   │   │   └── viewport-observer.ts
│   │   │   ├── extractors/                  # Content extractors
│   │   │   │   ├── text-extractor.ts
│   │   │   │   ├── image-extractor.ts
│   │   │   │   ├── video-extractor.ts
│   │   │   │   ├── form-extractor.ts
│   │   │   │   └── metadata-extractor.ts
│   │   │   ├── injectors/                   # UI injectors
│   │   │   │   ├── highlight-injector.ts
│   │   │   │   ├── tooltip-injector.ts
│   │   │   │   ├── overlay-injector.ts
│   │   │   │   └── sidebar-injector.ts
│   │   │   ├── handlers/                    # Event handlers
│   │   │   │   ├── click-handler.ts
│   │   │   │   ├── selection-handler.ts
│   │   │   │   ├── context-menu-handler.ts
│   │   │   │   └── keyboard-handler.ts
│   │   │   └── utils/
│   │   │       ├── dom-utils.ts
│   │   │       ├── sanitizer.ts
│   │   │       └── css-injector.ts
│   │   │
│   │   ├── popup/                           # Popup UI
│   │   │   ├── index.tsx                    # Entry point
│   │   │   ├── App.tsx                      # Root component
│   │   │   ├── components/
│   │   │   │   ├── QuickActions.tsx
│   │   │   │   ├── StatusIndicator.tsx
│   │   │   │   ├── ShortcutList.tsx
│   │   │   │   └── Settings/
│   │   │   │       ├── SettingsPanel.tsx
│   │   │   │       ├── ModelSelector.tsx
│   │   │   │       └── APIConfig.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useExtensionState.ts
│   │   │   │   ├── useAPI.ts
│   │   │   │   └── useSettings.ts
│   │   │   └── styles/
│   │   │       └── popup.css
│   │   │
│   │   ├── sidebar/                         # Sidebar UI
│   │   │   ├── index.tsx                    # Entry point
│   │   │   ├── App.tsx                      # Root component
│   │   │   ├── components/
│   │   │   │   ├── Chat/
│   │   │   │   │   ├── ChatInterface.tsx
│   │   │   │   │   ├── MessageList.tsx
│   │   │   │   │   ├── MessageItem.tsx
│   │   │   │   │   ├── InputBox.tsx
│   │   │   │   │   └── TypingIndicator.tsx
│   │   │   │   ├── Context/
│   │   │   │   │   ├── ContextPanel.tsx
│   │   │   │   │   ├── PageInfo.tsx
│   │   │   │   │   ├── SelectedContent.tsx
│   │   │   │   │   └── RelatedContent.tsx
│   │   │   │   ├── History/
│   │   │   │   │   ├── ConversationHistory.tsx
│   │   │   │   │   ├── SearchHistory.tsx
│   │   │   │   │   └── HistoryItem.tsx
│   │   │   │   └── Tools/
│   │   │   │       ├── ToolPanel.tsx
│   │   │   │       ├── ToolSelector.tsx
│   │   │   │       └── ToolResult.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useChat.ts
│   │   │   │   ├── useContext.ts
│   │   │   │   ├── useHistory.ts
│   │   │   │   └── useWebSocket.ts
│   │   │   └── styles/
│   │   │       └── sidebar.css
│   │   │
│   │   ├── options/                         # Options page
│   │   │   ├── index.tsx
│   │   │   ├── App.tsx
│   │   │   ├── components/
│   │   │   │   ├── GeneralSettings.tsx
│   │   │   │   ├── ModelSettings.tsx
│   │   │   │   ├── PrivacySettings.tsx
│   │   │   │   ├── AdvancedSettings.tsx
│   │   │   │   └── About.tsx
│   │   │   └── styles/
│   │   │       └── options.css
│   │   │
│   │   ├── shared/                          # Shared components & utilities
│   │   │   ├── components/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Select.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Toast.tsx
│   │   │   │   └── Spinner.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useLocalStorage.ts
│   │   │   │   ├── useDebounce.ts
│   │   │   │   ├── useThrottle.ts
│   │   │   │   └── useMediaQuery.ts
│   │   │   ├── utils/
│   │   │   │   ├── logger.ts
│   │   │   │   ├── crypto.ts
│   │   │   │   ├── validator.ts
│   │   │   │   ├── formatter.ts
│   │   │   │   └── constants.ts
│   │   │   ├── types/
│   │   │   │   ├── message.types.ts
│   │   │   │   ├── agent.types.ts
│   │   │   │   ├── tool.types.ts
│   │   │   │   └── api.types.ts
│   │   │   └── styles/
│   │   │       └── shared.css
│   │   │
│   │   └── workers/                         # Web workers
│   │       ├── embedding-worker.ts
│   │       ├── ocr-worker.ts
│   │       └── compression-worker.ts
│   │
│   ├── public/                              # Static assets
│   │   ├── icons/
│   │   │   ├── icon-16.png
│   │   │   ├── icon-48.png
│   │   │   └── icon-128.png
│   │   ├── _locales/                        # Internationalization
│   │   │   ├── en/
│   │   │   │   └── messages.json
│   │   │   └── vi/
│   │   │       └── messages.json
│   │   └── manifest.json                    # Extension manifest (V3)
│   │
│   ├── tests/                               # Extension tests
│   │   ├── unit/
│   │   │   ├── background/
│   │   │   ├── content/
│   │   │   └── shared/
│   │   ├── integration/
│   │   │   └── message-passing.test.ts
│   │   └── e2e/
│   │       ├── popup.test.ts
│   │       ├── sidebar.test.ts
│   │       └── content-script.test.ts
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── webpack.config.js                    # Build configuration
│   ├── .eslintrc.js
│   ├── .prettierrc
│   └── README.md
│
├── 📁 server/                               # Local AI Server (Backend - Python 3.11)
│   ├── src/
│   │   ├── api/                             # FastAPI application
│   │   │   ├── __init__.py
│   │   │   ├── main.py                      # FastAPI app entry
│   │   │   ├── deps.py                      # Dependencies injection
│   │   │   ├── middleware/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── cors.py
│   │   │   │   ├── rate_limit.py
│   │   │   │   ├── logging.py
│   │   │   │   └── error_handler.py
│   │   │   ├── routers/                     # API endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agents.py                # Agent endpoints
│   │   │   │   ├── chat.py                  # Chat endpoints
│   │   │   │   ├── tools.py                 # Tool endpoints
│   │   │   │   ├── memory.py                # Memory endpoints
│   │   │   │   ├── rag.py                   # RAG endpoints
│   │   │   │   ├── models.py                # Model management
│   │   │   │   └── health.py                # Health check
│   │   │   └── schemas/                     # Pydantic models
│   │   │       ├── __init__.py
│   │   │       ├── request.py
│   │   │       ├── response.py
│   │   │       ├── agent.py
│   │   │       ├── tool.py
│   │   │       └── memory.py
│   │   │
│   │   ├── agents/                          # Agent implementations
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # Base agent class
│   │   │   ├── registry.py                  # Agent registry
│   │   │   ├── factory.py                   # Agent factory
│   │   │   ├── research/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── research_agent.py
│   │   │   │   └── strategies/
│   │   │   │       ├── web_search.py
│   │   │   │       ├── multi_source.py
│   │   │   │       └── fact_verification.py
│   │   │   ├── content/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── content_agent.py
│   │   │   │   └── processors/
│   │   │   │       ├── extractor.py
│   │   │   │       ├── summarizer.py
│   │   │   │       └── translator.py
│   │   │   ├── vision/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vision_agent.py
│   │   │   │   └── models/
│   │   │   │       ├── ocr.py
│   │   │   │       ├── detector.py
│   │   │   │       └── captioner.py
│   │   │   ├── automation/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── automation_agent.py
│   │   │   │   └── workflows/
│   │   │   │       ├── form_filler.py
│   │   │   │       ├── browser_control.py
│   │   │   │       └── task_executor.py
│   │   │   ├── coding/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── coding_agent.py
│   │   │   │   └── capabilities/
│   │   │   │       ├── generator.py
│   │   │   │       ├── reviewer.py
│   │   │   │       └── debugger.py
│   │   │   ├── coordinator/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── coordinator_agent.py
│   │   │   │   ├── planner.py
│   │   │   │   ├── delegator.py
│   │   │   │   └── resolver.py
│   │   │   └── memory/
│   │   │       ├── __init__.py
│   │   │       ├── memory_agent.py
│   │   │       ├── short_term.py
│   │   │       ├── long_term.py
│   │   │       └── semantic.py
│   │   │
│   │   ├── core/                            # Core systems
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py              # Master orchestrator
│   │   │   ├── llm/                         # Language model layer
│   │   │   │   ├── __init__.py
│   │   │   │   ├── manager.py               # Model manager
│   │   │   │   ├── registry.py              # Model registry
│   │   │   │   ├── adapters/                # Model adapters
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── ollama.py
│   │   │   │   │   ├── llama_cpp.py
│   │   │   │   │   ├── vllm.py
│   │   │   │   │   └── transformers.py
│   │   │   │   ├── inference.py             # Inference engine
│   │   │   │   ├── quantization.py          # Quantization utils
│   │   │   │   └── cache.py                 # KV cache manager
│   │   │   ├── prompts/                     # Prompt engineering
│   │   │   │   ├── __init__.py
│   │   │   │   ├── manager.py
│   │   │   │   ├── templates/               # Jinja2 templates
│   │   │   │   │   ├── system_prompts/
│   │   │   │   │   ├── agent_prompts/
│   │   │   │   │   └── tool_prompts/
│   │   │   │   ├── builder.py               # Dynamic builder
│   │   │   │   └── optimizer.py             # Token optimizer
│   │   │   └── context/                     # Context management
│   │   │       ├── __init__.py
│   │   │       ├── manager.py
│   │   │       ├── window.py                # Context window
│   │   │       ├── compressor.py            # Compression
│   │   │       └── tokenizer.py             # Token counter
│   │   │
│   │   ├── tools/                           # Tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # Base tool class
│   │   │   ├── registry.py                  # Tool registry
│   │   │   ├── executor.py                  # Tool executor
│   │   │   ├── validator.py                 # Input validation
│   │   │   ├── web/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scraper.py
│   │   │   │   ├── search.py
│   │   │   │   ├── url_analyzer.py
│   │   │   │   └── dom_manipulator.py
│   │   │   ├── vision/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ocr.py
│   │   │   │   ├── object_detection.py
│   │   │   │   ├── image_classification.py
│   │   │   │   ├── screenshot.py
│   │   │   │   └── video_extractor.py
│   │   │   ├── code/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── executor.py              # Sandboxed execution
│   │   │   │   ├── validator.py
│   │   │   │   ├── formatter.py
│   │   │   │   └── parser.py
│   │   │   ├── data/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── file_io.py
│   │   │   │   ├── database.py
│   │   │   │   ├── transformer.py
│   │   │   │   └── calculator.py
│   │   │   └── browser/
│   │   │       ├── __init__.py
│   │   │       ├── tab_manager.py
│   │   │       ├── bookmark_organizer.py
│   │   │       ├── history_analyzer.py
│   │   │       └── form_filler.py
│   │   │
│   │   ├── rag/                             # RAG system
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py                  # Main RAG pipeline
│   │   │   ├── embeddings/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── manager.py
│   │   │   │   ├── models.py                # Embedding models
│   │   │   │   └── cache.py
│   │   │   ├── indexing/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── indexer.py
│   │   │   │   ├── chunker.py               # Text splitting
│   │   │   │   ├── metadata.py              # Metadata extraction
│   │   │   │   └── deduplicator.py
│   │   │   ├── retrieval/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── retriever.py
│   │   │   │   ├── dense.py                 # Dense retrieval
│   │   │   │   ├── sparse.py                # BM25
│   │   │   │   ├── hybrid.py                # Ensemble
│   │   │   │   └── reranker.py              # Cross-encoder
│   │   │   ├── query/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── processor.py
│   │   │   │   ├── expander.py              # Query expansion
│   │   │   │   └── rewriter.py
│   │   │   └── vector_store/
│   │   │       ├── __init__.py
│   │   │       ├── chroma.py                # ChromaDB client
│   │   │       ├── collections.py
│   │   │       └── search.py
│   │   │
│   │   ├── governance/                      # Governance & safety
│   │   │   ├── __init__.py
│   │   │   ├── moderation/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── input_filter.py
│   │   │   │   ├── output_filter.py
│   │   │   │   ├── pii_detector.py
│   │   │   │   └── guardrails.py
│   │   │   ├── security/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── encryption.py
│   │   │   │   ├── sanitizer.py
│   │   │   │   └── access_control.py
│   │   │   ├── privacy/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── anonymizer.py
│   │   │   │   ├── gdpr.py
│   │   │   │   └── audit.py
│   │   │   └── resource/
│   │   │       ├── __init__.py
│   │   │       ├── rate_limiter.py
│   │   │       ├── quota_manager.py
│   │   │       └── cost_tracker.py
│   │   │
│   │   ├── handoff/                         # Agent handoff & coordination
│   │   │   ├── __init__.py
│   │   │   ├── coordinator.py               # Handoff coordinator
│   │   │   ├── planner/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── task_decomposer.py
│   │   │   │   ├── dependency_graph.py
│   │   │   │   └── execution_planner.py
│   │   │   ├── router/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── capability_matcher.py
│   │   │   │   ├── load_balancer.py
│   │   │   │   └── fallback_handler.py
│   │   │   ├── communication/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── message_queue.py         # Redis pub/sub
│   │   │   │   ├── shared_memory.py
│   │   │   │   └── event_bus.py
│   │   │   ├── workflow/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── executor.py
│   │   │   │   ├── chain.py                 # Sequential
│   │   │   │   ├── parallel.py              # Parallel
│   │   │   │   └── conditional.py           # Routing
│   │   │   └── state/
│   │   │       ├── __init__.py
│   │   │       ├── session.py
│   │   │       ├── tracker.py
│   │   │       └── checkpoint.py
│   │   │
│   │   ├── memory/                          # Memory systems
│   │   │   ├── __init__.py
│   │   │   ├── manager.py
│   │   │   ├── short_term.py                # Redis-based
│   │   │   ├── long_term.py                 # Vector DB
│   │   │   ├── semantic.py                  # Knowledge
│   │   │   ├── procedural.py                # Skills
│   │   │   └── consolidator.py              # Memory consolidation
│   │   │
│   │   ├── monitoring/                      # Observability
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py                   # Prometheus
│   │   │   ├── logging.py                   # Structured logging
│   │   │   ├── tracing.py                   # OpenTelemetry
│   │   │   └── alerting.py
│   │   │
│   │   ├── data/                            # Data layer
│   │   │   ├── __init__.py
│   │   │   ├── database/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sqlite.py                # SQLite client
│   │   │   │   ├── models.py                # ORM models
│   │   │   │   └── migrations/              # Alembic migrations
│   │   │   ├── cache/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── redis_client.py
│   │   │   │   └── strategies.py
│   │   │   └── storage/
│   │   │       ├── __init__.py
│   │   │       ├── file_storage.py
│   │   │       └── model_storage.py
│   │   │
│   │   ├── config/                          # Configuration
│   │   │   ├── __init__.py
│   │   │   ├── settings.py                  # Pydantic settings
│   │   │   ├── models.yaml                  # Model configs
│   │   │   ├── agents.yaml                  # Agent configs
│   │   │   └── tools.yaml                   # Tool configs
│   │   │
│   │   └── utils/                           # Utilities
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── exceptions.py
│   │       ├── validators.py
│   │       ├── formatters.py
│   │       └── helpers.py
│   │
│   ├── tests/                               # Backend tests
│   │   ├── unit/
│   │   │   ├── agents/
│   │   │   ├── tools/
│   │   │   ├── rag/
│   │   │   └── core/
│   │   ├── integration/
│   │   │   ├── test_agent_coordination.py
│   │   │   ├── test_rag_pipeline.py
│   │   │   └── test_tool_execution.py
│   │   ├── e2e/
│   │   │   └── test_api_endpoints.py
│   │   └── conftest.py                      # Pytest fixtures
│   │
│   ├── scripts/                             # Utility scripts
│   │   ├── download_models.py
│   │   ├── setup_vector_db.py
│   │   ├── migrate_data.py
│   │   └── benchmark.py
│   │
│   ├── requirements/                        # Python dependencies
│   │   ├── base.txt                         # Base requirements
│   │   ├── dev.txt                          # Development
│   │   ├── test.txt                         # Testing
│   │   └── prod.txt                         # Production
│   │
│   ├── alembic/                             # Database migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   │
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml                       # Poetry config
│   ├── pytest.ini
│   ├── .env.example
│   └── README.md
│
├── 📁 models/                              # AI Models storage
│   ├── llm/                                 # Language models
│   │   ├── DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf
│   │   ├── DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf
│   │   └── Qwen3-14B-Q6_K.gguf
│   ├── embeddings/                          # Embedding models
│   │   └── all-MiniLM-L6-v2/
│   └── vision/                              # Vision models
│       ├── mmproj-Qwen_Qwen3-VL-8B-Instruct-bf16.gguf
│       └── Qwen_Qwen3-VL-8B-Instruct-Q8_0.gguf
│
├── 📁 data/                                 # Data storage
│   ├── vector_db/                           # ChromaDB data
│   ├── sqlite/                              # SQLite databases
│   ├── cache/                               # Cache files
│   └── logs/                                # Application logs
│
├── 📁 scripts/                              # Project-level scripts
│   ├── setup.sh                             # Initial setup
│   ├── dev.sh                               # Start dev environment
│   ├── build.sh                             # Build all components
│   ├── test.sh                              # Run all tests
│   └── deploy.sh                            # Deployment script
│
├── 📁 infrastructure/                       # Infrastructure as Code (future)
│   ├── docker/
│   │   ├── Dockerfile.server
│   │   ├── Dockerfile.dev
│   │   └── docker-compose.dev.yml
│   ├── kubernetes/                          # K8s manifests (future)
│   └── terraform/                           # Cloud resources (future)
│
├── 📁 monitoring/                           # Monitoring configs
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   └── dashboards/
│   └── loki/
│       └── loki-config.yml
│
├── .gitignore
├── .gitattributes
├── .editorconfig
├── .dockerignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── CODE_OF_CONDUCT.md
```

## Key Directory Purposes

### Extension Structure
- **background/**: Core business logic, state management, API communication
- **content/**: Web page interaction, content extraction, UI injection
- **popup/**: Quick access interface for immediate actions
- **sidebar/**: Main chat interface with full features
- **options/**: Comprehensive settings and configuration
- **shared/**: Reusable components, utilities, types across all UI contexts

### Server Structure
- **api/**: FastAPI application with routers, middleware, schemas
- **agents/**: All agent implementations organized by type
- **core/**: LLM management, prompt engineering, context handling
- **tools/**: Tool implementations organized by category
- **rag/**: Complete RAG pipeline (embedding, indexing, retrieval)
- **governance/**: Security, privacy, moderation, resource management
- **handoff/**: Agent coordination, task planning, workflow execution
- **memory/**: Different memory types and management
- **monitoring/**: Observability stack integration

### Data & Models
- **models/**: Pre-downloaded AI models (LLM, embeddings, vision)
- **data/**: Runtime data (vector DB, databases, caches, logs)

### Infrastructure
- **infrastructure/**: Docker, K8s, Terraform configs
- **monitoring/**: Prometheus, Grafana, Loki configurations
- **scripts/**: Automation scripts for development and deployment

## File Naming Conventions

- **Python**: `snake_case.py` (e.g., `research_agent.py`)
- **TypeScript/React**: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Config files**: `kebab-case.yml` or `lowercase.json`
- **Test files**: `test_*.py` or `*.test.ts`

## Import Path Examples

```python
# Python imports
from src.agents.research.research_agent import ResearchAgent
from src.core.llm.manager import LLMManager
from src.rag.pipeline import RAGPipeline
from src.tools.web.scraper import WebScraper
```

```typescript
// TypeScript imports
import { ChatInterface } from '@/sidebar/components/Chat/ChatInterface';
import { useExtensionState } from '@/shared/hooks/useExtensionState';
import { MessageType } from '@/shared/types/message.types';
import { localAIClient } from '@/background/api/local-ai-client';
```
