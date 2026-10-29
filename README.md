# 🛡️ AgentGuard: The Circuit Breaker & Safety Firewall for AI Agents

<p align="center">
  <a href="https://github.com/cuic19053-hue/agent-guard/stargazers"><img src="https://img.shields.io/github/stars/cuic19053-hue/agent-guard?style=for-the-badge&logo=github&color=00ffaa" alt="GitHub Stars"></a>
  <a href="https://pypi.org/project/agent-guard/"><img src="https://img.shields.io/pypi/v/agent-guard?style=for-the-badge&logo=pypi&color=blue" alt="PyPI Version"></a>
  <a href="https://github.com/cuic19053-hue/agent-guard/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge" alt="License"></a>
  <a href="https://hub.docker.com/r/agentguard/agent-guard"><img src="https://img.shields.io/docker/pulls/agentguard/agent-guard?style=for-the-badge&logo=docker" alt="Docker Pulls"></a>
  <a href="https://discord.gg/"><img src="https://img.shields.io/badge/Community-Discord-purple?style=for-the-badge&logo=discord" alt="Discord"></a>
</p>

<p align="center">
  <strong>Stop AI Agent Infinite Loops • Block Dangerous Tool Calls (rm -rf / Drop Table) • Auto Cut-Off API Budget Overrun</strong>
</p>

<p align="center">
  <em>Zero-Code Change. Plug-and-play reverse proxy for OpenAI, DeepSeek, Claude, Ollama, LangChain, CrewAI, AutoGen, and Dify.</em>
</p>

---

## ⚡ What is AgentGuard?

**AgentGuard** is an open-source, ultra-lightweight **runtime circuit breaker and security gateway** designed specifically for autonomous AI Agents and LLM Function Calling.

When you give an AI agent access to tools (Bash, Python REPL, SQL database, Web scraping), things can quickly spiral out of control:
1. 💸 **Infinite Retry Loop**: The agent fails a step and retries 50 times in 2 minutes, burning **$500+ in OpenAI API tokens**.
2. 💣 **Destructive Tool Execution**: The agent hallucinates and executes dangerous commands like `rm -rf /`, `DROP TABLE users;`, or leaks sensitive `.env` keys.
3. 🐌 **Context Window Explosion**: Multi-turn history grows uncontrollably to 128k tokens, driving latency through the roof.

**AgentGuard acts as an intelligent safety proxy.** Just change your agent's `base_url` to `http://localhost:8080/v1`—AgentGuard intercepts all traffic, detects loops in real time, blocks unauthorized tools, and protects your server and wallet.

---

## 🚀 Quick Start (5 Seconds)

### 1. Run AgentGuard with Pip or Docker

```bash
# Option A: Run via Python CLI
pip install agent-guard
agent-guard --port 8080 --target-url https://api.openai.com

# Option B: Run via Docker (Zero-dependency)
docker run -d -p 8080:8080 \
  -e TARGET_URL=https://api.openai.com \
  agentguard/agent-guard:latest
```

### 2. Point Your Agent to AgentGuard (Zero Code Change!)

Simply point your existing OpenAI / LangChain / CrewAI client to `localhost:8080`:

#### In Python:
```python
from openai import OpenAI

# Simply change base_url to AgentGuard!
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="sk-your-openai-or-deepseek-key"
)

response = client.chat.completions.create(
    model="gpt-4o",  # or deepseek-chat, claude-3-5-sonnet
    messages=[{"role": "user", "content": "Analyze system logs"}],
    tools=my_agent_tools
)
```

#### In LangChain / CrewAI / AutoGen:
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    base_url="http://localhost:8080/v1",
    api_key="sk-..."
)
```

---

## 🛡️ Key Features

### 1. 🔄 Dead-Loop Sentinel (Stop Agent Infinite Loops)
- Tracks agent conversation fingerprint and sliding window tool calls.
- Detects recurring identical tool calls with same parameters.
- **Auto-trips the circuit breaker** on the 3rd failed attempt and injects graceful correction prompts, preventing runaway API bills.

### 2. 🚫 Dangerous Tool Call Interceptor (Block rm -rf & Drop Tables)
- Real-time static analysis and regex protection for Function / Tool Calls.
- Pre-configured guardrails for:
  - **Bash/Shell**: Blocks `rm -rf`, `mkfs`, `dd`, `chmod 777`, `kill -9`.
  - **SQL**: Blocks `DROP DATABASE`, `TRUNCATE`, `ALTER TABLE` unless explicitly allowed.
  - **File Operations**: Prevents path traversal (`../../etc/passwd`).
- Optional **Human-in-the-Loop Webhook** (Slack / Discord / Lark approval button).

### 3. 💰 Budget Hard Cap & Token Circuit Breaker
- Set a maximum USD or token budget per session or per minute.
- Returns an immediate `429 TokenBudgetExceeded` error the moment an agent goes rogue.

### 4. 🗜️ Context Window Pruning (Save 30% - 50% Tokens)
- Strips repetitive failure stack traces and excessive whitespaces before sending them to the model.
- Lowers token consumption and boosts response speeds.

---

## 🔍 How It Compares

| Feature | AgentGuard | LiteLLM | NeMo Guardrails | Langfuse |
| :--- | :---: | :---: | :---: | :---: |
| **Agent Infinite Loop Breaker** | ✅ **Native** | ❌ No | ❌ Complex setup | ❌ Post-facto only |
| **Dangerous Tool Interception** | ✅ **Out-of-the-box** | ❌ No | ⚠️ Requires Colang | ❌ Observability only |
| **Zero-Code Integration (`base_url`)** | ✅ **Yes** | ✅ Yes | ❌ No | ❌ Requires SDK wrapping |
| **Installation Overhead** | ⚡ **< 5MB / Single binary** | 📦 Medium | 🐘 Heavy (Needs PyTorch/Models) | ☁️ Needs Cloud / DB |
| **Streaming (SSE) Support** | ✅ **Real-time** | ✅ Yes | ⚠️ Partial | ✅ Yes |

---

## ⚙️ Configuration (`agentguard.yaml`)

Create an optional `agentguard.yaml` in your project root:

```yaml
server:
  port: 8080
  target_url: "https://api.openai.com"  # or https://api.deepseek.com

circuit_breaker:
  enabled: true
  max_repeated_tool_calls: 3        # Break if tool is called 3 times with same params
  max_session_turns: 25             # Max interaction turns per task
  hard_budget_tokens: 100000        # Max tokens allowed per session

security:
  block_dangerous_tools: true
  blocked_patterns:
    - "rm\\s+-rf"
    - "drop\\s+table"
    - "truncate"
    - "chmod\\s+777"
  human_in_the_loop:
    enabled: false
    webhook_url: "https://hooks.slack.com/services/..."
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

## 🤝 Contributing & Community

We welcome all contributions! Whether it's adding safety rules, enhancing protocol parsers, or writing documentation.

- 🐛 [Report Bugs & Feature Requests](https://github.com/cuic19053-hue/agent-guard/issues)
- 💡 [Submit a Pull Request](https://github.com/cuic19053-hue/agent-guard/pulls)

---

## 📄 License

AgentGuard is licensed under the [Apache 2.0 License](LICENSE).
