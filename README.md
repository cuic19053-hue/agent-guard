<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/cuic19053-hue/agent-guard/main/assets/banner.png">
    <img alt="AgentGuard Banner" src="https://raw.githubusercontent.com/cuic19053-hue/agent-guard/main/assets/banner.png" width="100%">
  </picture>
</p>

# 🛡️ AgentGuard

<p align="center">
  <strong>The Circuit Breaker & Safety Firewall for AI Agents and LLM Function Calling.</strong>
</p>

<p align="center">
  <a href="https://github.com/cuic19053-hue/agent-guard/stargazers"><img src="https://img.shields.io/github/stars/cuic19053-hue/agent-guard?style=for-the-badge&logo=github&color=00ffaa" alt="GitHub Stars"></a>
  <a href="https://github.com/cuic19053-hue/agent-guard/network/members"><img src="https://img.shields.io/github/forks/cuic19053-hue/agent-guard?style=for-the-badge&logo=github&color=blue" alt="GitHub Forks"></a>
  <a href="https://pypi.org/project/agent-guard/"><img src="https://img.shields.io/pypi/v/agent-guard?style=for-the-badge&logo=pypi&color=blue" alt="PyPI Version"></a>
  <a href="https://github.com/cuic19053-hue/agent-guard/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge" alt="License"></a>
  <a href="https://github.com/cuic19053-hue/agent-guard/issues"><img src="https://img.shields.io/github/issues/cuic19053-hue/agent-guard?style=for-the-badge&color=orange" alt="GitHub Issues"></a>
  <a href="https://hub.docker.com/r/cuic19053/agent-guard"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" alt="Docker Pulls"></a>
</p>

<p align="center">
  <strong>Stop Runaway AI Agent Loops • Block Dangerous Tool Calls (`rm -rf` / `DROP TABLE`) • Auto-Halt API Token Budget Burn</strong>
</p>

<p align="center">
  <em>Zero Code Modification. Plug-and-play reverse proxy for OpenAI, DeepSeek, Claude, Ollama, LangChain, CrewAI, AutoGen, and Dify.</em>
</p>

---

## ⚡ The Nightmare AgentGuard Solves

When autonomous AI agents gain tool execution capabilities (Bash commands, Python REPL, SQL databases, Web scrapers), production risks multiply overnight:

```text
       [Your Agent] 
            │  (base_url = localhost:8080/v1)
            ▼
    ┌──────────────────────────────────────────────┐
    │              🛡️ AgentGuard                   │
    │  ├─ 🔄 Dead-Loop Breaker (Repeated tools)    │
    │  ├─ 🚫 Dangerous Command Shield (rm -rf)    │
    │  └─ 💰 Budget & Token Hard-Cap Sentry       │
    └──────────────────────────────────────────────┘
            │
            ▼
   [OpenAI / DeepSeek / Claude / Local Ollama]
```

* 💸 **Infinite Retry Loop (Token Burn)**: An agent hits a missing file or a 404 URL and retries 50 times in 2 minutes, draining **$500+ in API credits**.
* 💣 **Destructive Tool Execution (System Wipeout)**: The agent hallucinates and executes dangerous commands like `rm -rf /*`, `DROP TABLE users;`, or alters system permissions.
* 🐌 **Context Window Explosion**: Multi-turn history grows uncontrollably to 128k+ tokens, destroying response latency and blowing budgets.

**AgentGuard acts as an intelligent safety gatekeeper.** Just point your agent's `base_url` to `http://localhost:8080/v1`. AgentGuard monitors traffic in real time, auto-trips the breaker on infinite loops, and blocks hazardous operations before damage occurs.

---

## 🚀 Quick Start (Under 60 Seconds)

### 1. Start AgentGuard via Python CLI or Docker

```bash
# Option A: Run via pip CLI
pip install agent-guard
agent-guard --port 8080 --target-url https://api.openai.com

# Option B: Run via Docker (Zero-dependency)
docker run -d -p 8080:8080 \
  -e TARGET_URL=https://api.openai.com \
  agentguard/agent-guard:latest
```

### 2. Connect Your Agent (Zero Code Changes!)

Simply change the `base_url` in your existing SDK:

#### Python (Official OpenAI / DeepSeek SDK)
```python
from openai import OpenAI

# Simply route through AgentGuard!
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="sk-your-openai-or-deepseek-key"
)

response = client.chat.completions.create(
    model="gpt-4o",  # or deepseek-chat, claude-3-5-sonnet
    messages=[{"role": "user", "content": "Analyze database logs"}],
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

## 🛡️ Core Capabilities

### 1. 🔄 Dead-Loop Sentinel (Automated Circuit Breaker)
* Monitors session fingerprints and sliding-window tool executions.
* Detects cyclical, identical tool invocations with identical arguments.
* **Auto-trips on the 3rd attempt**, halting runaway loops and preventing catastrophic API bills.

### 2. 🚫 Dangerous Tool Call Interception (`rm -rf`, `DROP TABLE`)
* Real-time static analysis and regex protection for Function / Tool Calling.
* Default protection suite:
  * **Bash / Shell**: Intercepts `rm -rf`, `mkfs`, `dd`, `chmod 777`, `kill -9`.
  * **SQL Database**: Blocks `DROP DATABASE`, `TRUNCATE`, `ALTER TABLE` unless whitelisted.
  * **File Systems**: Prevents directory traversal (`../../etc/passwd`).

### 3. 💰 Budget Hard-Cap & Rate Guard
* Configure token and cost budgets per session or timeframe.
* Returns standard `429 circuit_breaker_tripped` the moment abnormal consumption patterns emerge.

### 4. 🗜️ Context Window Optimization
* Strips redundant execution traces, noisy terminal logs, and whitespace bloating prior to upstream forwarding.
* Saves 30%–50% in token overhead while reducing round-trip latency.

---

## 🔍 How AgentGuard Compares

| Feature | AgentGuard | LiteLLM | NeMo Guardrails | Langfuse |
| :--- | :---: | :---: | :---: | :---: |
| **Agent Infinite Loop Breaker** | ✅ **Native** | ❌ No | ❌ Complex setup | ❌ Post-facto only |
| **Dangerous Tool Interception** | ✅ **Out-of-the-box** | ❌ No | ⚠️ Requires Colang | ❌ Observability only |
| **Zero-Code Integration (`base_url`)** | ✅ **Yes** | ✅ Yes | ❌ No | ❌ Requires SDK wrapping |
| **Installation Overhead** | ⚡ **< 5MB / Single binary** | 📦 Medium | 🐘 Heavy (Needs PyTorch/Models) | ☁️ Needs Cloud / DB |
| **Streaming (SSE) Support** | ✅ **Real-time** | ✅ Yes | ⚠️ Partial | ✅ Yes |

---

## ⚙️ Configuration (`agentguard.yaml`)

Customize rules easily in your root directory:

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  target_url: "https://api.openai.com"  # or https://api.deepseek.com

circuit_breaker:
  enabled: true
  max_repeated_tool_calls: 3        # Tripped if identical tool is called 3 times
  max_session_turns: 30             # Maximum dialog turns per session
  hard_budget_tokens: 150000        # Token ceiling per session

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

## 🗺️ Roadmap

- [x] Zero-config OpenAI-compatible Reverse Proxy (Streaming & Non-Streaming)
- [x] Sliding-window Dead-Loop Detection State Machine
- [x] Tool-Call AST & Regex Security Guardrails
- [ ] Webhook Human-in-the-Loop approval for high-risk operations
- [ ] Web UI Dashboard for real-time agent observability & trace playback
- [ ] Context pruning & semantic deduplication engine

---

## 🤝 Contributing

Contributions are warmly welcome! From safety heuristics to performance enhancements:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the Apache 2.0 License. See `LICENSE` for details.
