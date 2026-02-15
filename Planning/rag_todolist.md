# 🚀 Project Upgrade: Luna Multi-Agent System (MAS)

**Objective:** Transform Luna from a single-prompt generalist into a "Router-Based" system that dynamically switches between specialized "Agents" (Research, Code, Vision) based on user intent.

**Architecture:**
1.  **Router:** Analyzes input -> Selects the best Agent.
2.  **Agents:** Specialized System Prompts + Specific Tool Access.
3.  **Manager:** Executes the chosen Agent's configuration.


# 🚀 Project Upgrade: Luna Multi-Agent System (MAS)

**Objective:** Transform Luna from a single-prompt generalist into a "Router-Based" system that dynamically switches between specialized "Agents" (Research, Code, Vision) based on user intent.

**Architecture:**
1.  **Router:** Analyzes input -> Selects the best Agent.
2.  **Agents:** Specialized System Prompts + Specific Tool Access.
3.  **Manager:** Executes the chosen Agent's configuration.

---

## 📂 Phase 1: Define the Specialists (Prompts)
We need to give Luna "multiple personalities" optimized for specific tasks.

- [ ] **Create new file:** `server/src/core/prompts/templates/agents.py`
    - [ ] **Define `AGENT_RESEARCHER`:**
        -   *Goal:* Fact-based, objective, aggressive use of `<cmd_browser>`.
        -   *Constraint:* "Do not answer from memory. Always verify with search."
    - [ ] **Define `AGENT_CODER`:**
        -   *Goal:* High-performance code generation.
        -   *Constraint:* "Output only code blocks. No conversational filler. Use Python type hinting."
    - [ ] **Define `AGENT_VISION`:**
        -   *Goal:* Image analysis (already partially drafted).
        -   *Constraint:* "Describe visual details extensively before answering."
    - [ ] **Define `AGENT_ROUTER`:**
        -   *Goal:* A tiny prompt used to classify the user's intent.
        -   *Output:* Returns a JSON or keyword (e.g., "SEARCH", "CODE", "CHAT", "VISION").

---

## 📂 Phase 2: Build the Router Logic
The "Router" is the receptionist that directs the traffic.

- [ ] **Create new file:** `server/src/agents/router.py`
    - [ ] **Import:** Your LLM Manager and the new prompt templates.
    - [ ] **Create Class `IntentRouter`:**
        -   *Function `detect_intent(message, image)`:*
            -   **Rule 1 (Hard):** If `image` is present -> Return `VISION`.
            -   **Rule 2 (Keyword):** If message contains "search", "find", "price", "news" -> Return `SEARCH`.
            -   **Rule 3 (LLM):** For ambiguous queries, do a fast, low-temp LLM call to `AGENT_ROUTER` prompt to classify intent.
    - [ ] **Create Class `AgentConfig`:**
        -   Should return a dictionary containing:
            -   `system_prompt`: (The text from Phase 1)
            -   `model_name`: (e.g., "mistral" for Chat, "qwen2.5-vl" for Vision, "deepseek-coder" for Code)
            -   `temperature`: (0.7 for Chat, 0.1 for Code)

---

## 📂 Phase 3: Upgrade the Brain (LLM Manager)
Refactor the manager to stop using the one hardcoded `CORE_SYSTEM_PROMPT` and accept dynamic ones.

- [ ] **Modify file:** `server/src/core/llm/manager.py`
    - [ ] **Update `__init__`:** Remove hardcoded system prompt loading if present.
    - [ ] **Update `chat()` method:**
        -   Add argument: `agent_config: dict`.
        -   **Logic Change:** Instead of using `self.system_prompt`, use `agent_config['system_prompt']`.
        -   **Logic Change:** Instead of using `self.model`, use `agent_config['model_name']`.
        -   **Logic Change:** Inject `temperature` from the config.

---

## 📂 Phase 4: Wire the API Endpoint
Connect the Router to the actual API so the Frontend talks to the Router first.

- [ ] **Modify file:** `server/src/api/routers/chat.py`
    - [ ] **Import:** `IntentRouter` from `src/agents/router`.
    - [ ] **Initialize:** Create a global instance of `router = IntentRouter()`.
    - [ ] **Update `chat_endpoint` function:**
        1.  **Receive Request:** Get `user_message` and `image` from body.
        2.  **Route:** Call `selected_agent = router.detect_intent(user_message, image)`.
        3.  **Log:** Print to console: `f"🤖 Routing to: {selected_agent['name']}"`.
        4.  **Execute:** Call `llm_manager.chat(..., agent_config=selected_agent)`.

---

## 📂 Phase 5: Testing & Verification
- [ ] **Test Vision:** Upload an image.
    -   *Expected Log:* "🤖 Routing to: VISION"
    -   *Expected Model:* `qwen2.5-vl` (or your vision model).
- [ ] **Test Search:** Ask "What is the stock price of NVDA?"
    -   *Expected Log:* "🤖 Routing to: RESEARCHER"
    -   *Expected Behavior:* Immediate `<cmd_browser>` trigger.
- [ ] **Test Code:** Ask "Write a Python script for..."
    -   *Expected Log:* "🤖 Routing to: CODER"
    -   *Expected Output:* Clean code, no fluff.

---

## 💡 Future "Pro" Ideas (Backlog)
- [ ] **Agent Handoff:** Allow the "Researcher" to pass findings to the "Writer" (Sequential Chain).
- [ ] **UI Update:** Send the "Agent Name" back to the frontend so the Sidebar shows "Luna (Researcher)" instead of just "Luna".
---

## 📂 Target Folder Structure
This plan introduces a new `agents/` directory to keep logic clean and separates "Prompts" from "Logic".

```text
server/
└── src/
    ├── agents/                 # 🟢 NEW: The "Staff" Department
    │   ├── __init__.py         # Exposes the Router
    │   ├── router.py           # The "Manager": Decides which agent to use
    │   └── types.py            # Definitions: What is an "Agent"? (Config structure)
    │
    ├── api/
    │   └── routers/
    │       └── chat.py         # 🟡 UPDATE: Connects API to the Router (not just LLM)
    │
    ├── core/
    │   ├── llm/
    │   │   └── manager.py      # 🟡 UPDATE: Accepts dynamic system prompts
    │   │
    │   └── prompts/
    │       └── templates/
    │           ├── system.py   # (Keep: The default "Generalist" prompt)
    │           └── agents.py   # 🟢 NEW: The specialized prompts (Coder, Researcher, Vision)
    │
    └── main.py

