<div align="center">

# 🛡️ AgentGuard

### The Zero-Config Circuit Breaker & Safety Firewall for AI Agents

**Stop Runaway Agent Loops • Intercept Dangerous Tool Calls (`rm -rf` / `DROP TABLE`) • Cut Off Token Budget Burn**

<p align="center">
  <a href="https://github.com/cuic19053-hue/agent-guard/stargazers"><img src="https://img.shields.io/github/stars/cuic19053-hue/agent-guard?style=for-the-badge&logo=github&color=00ffaa" alt="GitHub Stars"></a>
  <a href="https://github.com/cuic19053-hue/agent-guard/network/members"><img src="https://img.shields.io/github/forks/cuic19053-hue/agent-guard?style=for-the-badge&logo=github&color=blue" alt="GitHub Forks"></a>
  <a href="https://pypi.org/project/agent-guard/"><img src="https://img.shields.io/badge/pypi-v0.1.0-blue?style=for-the-badge&logo=pypi" alt="PyPI Version"></a>
  <a href="https://github.com/cuic19053-hue/agent-guard/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge" alt="License"></a>
  <a href="https://github.com/cuic19053-hue/agent-guard/actions"><img src="https://img.shields.io/badge/tests-passing-success?style=for-the-badge&logo=pytest" alt="Tests"></a>
  <a href="https://hub.docker.com/r/cuic19053/agent-guard"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" alt="Docker Ready"></a>
</p>

*Zero Code Modification. Plug-and-play reverse proxy for OpenAI, DeepSeek, Claude, Ollama, LangChain, CrewAI, AutoGen, and Dify.*

---

</div>

## 📌 Why AgentGuard? (The Autonomous Agent Dilemma)

When developers give autonomous AI agents access to tools (Bash, Python REPL, SQL database, Web search), production agents inevitably face 3 catastrophic edge cases:

```text
               ┌───────────────────────┐
               │    Autonomous Agent   │ (LangChain / CrewAI / AutoGen)
               └───────────┬───────────┘
                           │ (base_url = http://localhost:8080/v1)
                           ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                      🛡️ AgentGuard                          │
 │                                                             │
 │  [1. Dead-Loop Sentinel]        [2. Dangerous Command Wall] │
 │   Identical Tool Call > 3?       Regex / AST Check          │
 │   ──► ⚡ Auto Trip & Halt        (rm -rf, DROP TABLE, ...)  │
 │                                  ──► 🚨 403 Forbidden       │
 │                                                             │
 │  [3. Token Sentry]                                          │
 │   Hard-cap budget ceiling reached? ──► 🛑 429 Terminate     │
 └─────────────────────────┬───────────────────────────────────┘
                           │ Safe traffic forward
                           ▼
          [OpenAI / DeepSeek / Claude / Ollama]
```

1. 💸 **The Infinite Retry Loop**: The agent hits a 404 or missing file and retries 50 times in 2 minutes, burning **$500+ in API credits**.
2. 💣 **Destructive Tool Execution**: The agent hallucinates and executes dangerous commands like `rm -rf /*`, `DROP TABLE users;`, or corrupts directories.
3. 🐌 **Context Window Explosion**: Multi-turn history grows uncontrollably to 128k+ tokens, destroying response latency and blowing budgets.

---

## ⚡ Quick Start (Under 60 Seconds)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/cuic19053-hue/agent-guard.git
cd agent-guard

# Install in editable mode
pip install -e .
```

### 2. Start the Gateway Proxy

```bash
# Point upstream target to OpenAI or DeepSeek
agent-guard --port 8080 --target-url https://api.openai.com
```

### 3. Point Your Agent to AgentGuard (Zero Code Change!)

Simply update `base_url` to `http://localhost:8080/v1`:

#### Python (OpenAI / DeepSeek SDK)
```python
from openai import OpenAI

# Zero code rewrite: Just point base_url to AgentGuard
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="sk-your-openai-or-deepseek-key"
)

response = client.chat.completions.create(
    model="gpt-4o",  # or deepseek-chat
    messages=[{"role": "user", "content": "Analyze system server logs"}],
    tools=my_agent_tools
)
```

#### LangChain / CrewAI / AutoGen
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    base_url="http://localhost:8080/v1",
    api_key="sk-..."
)
```

---

## 🧪 Live Simulation Demo

Run our included interactive end-to-end demonstration:

```bash
python examples/demo_agent.py
```

**Real output:**
```text
=================================================================
🛡️  AgentGuard Live Simulation & Demonstration
=================================================================

[Step 1: Normal Agent Execution]
👉 Agent calls tool: fetch_weather({"city": "San Francisco"})
✅ Status: ALLOWED (Dangerous: False, Loop Count: 1)

[Step 2: Dangerous Tool Call Interception]
👉 Rogue Agent attempts: execute_bash({"cmd": "rm -rf /var/data"})
🚨 [BLOCKED BY AGENTGUARD] Reason: Blocked dangerous command matching pattern: rm\s+-rf
🛡️  Result: 403 Forbidden returned to Agent! System wiped prevented.

[Step 3: Infinite Retry Loop & Circuit Breaker]
⚠️  Attempt 1: Agent retrying search_database... (Recorded count=1)
⚠️  Attempt 2: Agent retrying search_database... (Recorded count=2)
⚡ [CIRCUIT BREAKER TRIPPED at Attempt 3]
🛑 Reason: Identical tool call repeated 3 times.
💰 Result: 429 CircuitBreakerTripped returned! Upstream API credit saved.
=================================================================
```

---

## 🛡️ Core Safeguards

| Feature | AgentGuard | LiteLLM | NeMo Guardrails | Langfuse |
| :--- | :---: | :---: | :---: | :---: |
| **Agent Infinite Loop Breaker** | ✅ **Native** | ❌ No | ❌ Complex setup | ❌ Post-facto only |
| **Dangerous Tool Interception** | ✅ **Out-of-the-box** | ❌ No | ⚠️ Requires Colang | ❌ Observability only |
| **Zero-Code Integration (`base_url`)** | ✅ **Yes** | ✅ Yes | ❌ No | ❌ Requires SDK wrapping |
| **Installation Overhead** | ⚡ **< 5MB / Single binary** | 📦 Medium | 🐘 Heavy (Needs PyTorch/Models) | ☁️ Needs Cloud / DB |
| **Streaming (SSE) Support** | ✅ **Real-time** | ✅ Yes | ⚠️ Partial | ✅ Yes |

---

## ⚙️ Configuration (`agentguard.yaml`)

You can customize loop thresholds and security regex patterns in `agentguard.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  target_url: "https://api.openai.com"

circuit_breaker:
  enabled: true
  max_repeated_tool_calls: 3        # Break loop on attempt 3
  max_session_turns: 30             # Maximum conversation turns
  hard_budget_tokens: 150000        # Max tokens per session

security:
  block_dangerous_tools: true
  blocked_patterns:
    - "rm\\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)"
    - "drop\\s+database"
    - "drop\\s+table"
    - "truncate\\s+table"
    - "chmod\\s+777"
```

---

## 🧪 Testing

Run comprehensive unit tests and proxy e2e tests:

```bash
pytest
```

---

## 📄 License

AgentGuard is open-sourced under the [Apache 2.0 License](LICENSE).
