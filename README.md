<div align="center">

# 🛡️ AgentGuard

### *The Production Circuit Breaker & Safety Sentry for Autonomous AI Agents*

[![GitHub Stars](https://img.shields.io/github/stars/cuic19053-hue/agent-guard?style=for-the-badge&logo=github&color=00ffaa)](https://github.com/cuic19053-hue/agent-guard/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/cuic19053-hue/agent-guard?style=for-the-badge&logo=github&color=blue)](https://github.com/cuic19053-hue/agent-guard/network/members)
[![PyPI Version](https://img.shields.io/badge/pypi-v0.1.0-blue?style=for-the-badge&logo=pypi)](https://pypi.org/project/agent-guard/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](https://github.com/cuic19053-hue/agent-guard/blob/main/LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-passing-success?style=for-the-badge&logo=pytest)](https://github.com/cuic19053-hue/agent-guard/actions)
[![Docker Ready](https://hub.docker.com/r/cuic19053/agent-guard)

<br/>

**English** | [简体中文](README_CN.md)(https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)](https://hub.docker.com/r/cuic19053/agent-guard)

<br/>

**One proxy line to stop runaway agent loops, prevent catastrophic `rm -rf /` catastrophes, and save thousands in API token bills.**

*Zero SDK rewrite • Sub-millisecond latency • Native OpenAI, Claude & DeepSeek API wire-compatible*

<br/>

```bash
# 5 seconds to immunity
pip install agent-guard
agent-guard --port 8080 --target-url https://api.openai.com
```

---

</div>

## 💥 The Real Incident (Why This Repo Exists)

> *"Last night, my autonomous coding agent got stuck on a 404 URL while researching documentation. It spun in an infinite retry loop 240 times in under 3 minutes, incinerating **$420 in OpenAI API credits** while I was asleep."*

> *"During local agent development, our LangChain agent attempted to clean up temporary workspace files and hallucinated `rm -rf /` directly into the local host container."*

Every engineer putting AI Agents (LangChain, CrewAI, AutoGen, Dify, Cursor) into production discovers two uncomfortable realities:
1. **Agents are fundamentally non-deterministic state machines.** When a tool call errors out, their instinct is to retry—endlessly.
2. **Current API gateways only count tokens after they are spent.** Nobody pulls the fire alarm *while* the fire is raging.

**AgentGuard is the missing circuit breaker.** It sits between your agent runtime and your LLM provider as a zero-latency reverse proxy, monitoring execution graphs in real time and tripping the breaker the millisecond anomaly patterns appear.

---

## 🎬 Live In Action (What It Actually Looks Like)

```text
========================================================================================
🛡️  AGENTGUARD RUNTIME SENTRY INTERCEPTION LOG
========================================================================================

[AGENT ATTEMPT 1] ──► tool_call: search_db({"query": "err_404_key"}) ──► ⚠️ Tool Failed
[AGENT ATTEMPT 2] ──► tool_call: search_db({"query": "err_404_key"}) ──► ⚠️ Tool Retrying
[AGENT ATTEMPT 3] ──► tool_call: search_db({"query": "err_404_key"}) ──► ⚡ [CIRCUIT BREAKER TRIPPED]

🛑 [AGENTGUARD INTERCEPT]: Repeated identical tool invocation (attempt 3/3).
💰 [SAVED]: Terminated session. Prevented estimated $140.00 in runaway recursive tokens.
📡 [STATUS]: Returned HTTP 429 { "error": "circuit_breaker_tripped" } to Agent Runtime.

----------------------------------------------------------------------------------------
[AGENT ATTEMPT 4] ──► tool_call: execute_bash({"cmd": "rm -rf /var/data"})
🚨 [AGENTGUARD BLOCKED]: Destructive pattern 'rm -rf' detected in function arguments!
🛡️  [PREVENTED]: Critical system wipe halted. Returned HTTP 403 Forbidden.
========================================================================================
```

---

## 🏗️ Architecture: Zero-Code Ingestion

You change **literally one line** in your existing codebase. No new client SDKs to learn, no vendor lock-in.

```text
  ┌────────────────────────────────────────────────────────┐
  │         Your AI Agent (CrewAI / LangChain / Raw)       │
  └───────────────────────────┬────────────────────────────┘
                              │
                              │ HTTP / SSE Stream
                              │ base_url = "http://localhost:8080/v1"
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                 🛡️ AGENTGUARD GATEWAY                  │
  │                                                        │
  │  ┌───────────────────────┐   ┌──────────────────────┐  │
  │  │  Dead-Loop Sentinel   │   │  Security Interceptor│  │
  │  │  Sliding Window Hash  │   │  AST & Regex Shield  │  │
  │  └───────────┬───────────┘   └───────────┬──────────┘  │
  │              │                           │             │
  │              ▼                           ▼             │
  │         [Pass / Trip]               [Safe / Block]     │
  └───────────────────────────┬────────────────────────────┘
                              │
                              │ Forward only validated traffic
                              ▼
        [OpenAI / DeepSeek / Claude / Local Ollama]
```

---

## ⚡ 60-Second Setup

### Step 1: Launch AgentGuard

```bash
# Via pip
pip install agent-guard
agent-guard --port 8080 --target-url https://api.openai.com

# Or single-command Docker
docker run -d -p 8080:8080 \
  -e TARGET_URL=https://api.openai.com \
  agentguard/agent-guard:latest
```

### Step 2: Swap One Parameter

#### 🐍 Native OpenAI / DeepSeek Python SDK
```python
from openai import OpenAI

# Simply change base_url. Everything else remains identical!
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="sk-your-upstream-key"
)

# Works out of the box with your existing tool-calling pipelines
response = client.chat.completions.create(
    model="gpt-4o",  # or deepseek-chat
    messages=[{"role": "user", "content": "Clean up cached build artifacts"}],
    tools=my_system_tools
)
```

#### 🦜️🔗 LangChain / CrewAI / AutoGen
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    base_url="http://localhost:8080/v1",
    api_key="sk-..."
)
```

---

## 🛡️ Core Defense Matrix

### 1. 🔄 Dead-Loop Sentinel (The Anti-Burn Breaker)
* **Fingerprint Window**: Computes normalized canonical parameter hashes across sliding call windows.
* **Auto-Trip Threshold**: If an agent calls the identical tool with invariant arguments 3 times, AgentGuard interrupts the loop immediately and returns an explicit `429 circuit_breaker_tripped` status code.
* **Adaptive Prompt Injection** *(Upcoming)*: Automatically injects hint instructions to nudge the model out of recursion before breaking.

### 2. 🚫 Destructive Tool Execution Firewall
* Real-time static analysis on outbound tool call argument payloads.
* Built-in zero-day defense rules:
  * **Shell Execution**: `rm -rf`, `mkfs`, `dd`, `chmod 777`, `kill -9`, fork bombs (`:(){ :|:& };:`).
  * **Database**: `DROP DATABASE`, `DROP TABLE`, `TRUNCATE`, bulk unindexed `DELETE`.
  * **Path Traversal**: Arbitrary sensitive reads (`/etc/passwd`, `~/.ssh/id_rsa`, `.env`).

### 3. 💰 Session Hard-Budget Ceiling
* Enforces strict per-task or per-session token caps (e.g., hard stop at 100k tokens).
* Eliminates the risk of runaway compound agent workflows accumulating unnoticed costs.

---

## 📊 Feature Comparison: Why Existing Tools Aren't Enough

| Requirement | 🛡️ AgentGuard | LiteLLM | NeMo Guardrails | Langfuse |
| :--- | :---: | :---: | :---: | :---: |
| **Real-time Infinite Loop Breaker** | **✅ Native Real-time** | ❌ No | ❌ Complex / No | ❌ Post-facto only |
| **Dangerous Command Shield (`rm -rf`)** | **✅ Zero-Config** | ❌ No | ⚠️ Requires Colang | ❌ Observability only |
| **Integration Complexity** | **⚡ 1 config line (`base_url`)** | ✅ 1 line | 🐘 High (Custom DSL) | 📦 SDK code wrapping |
| **Runtime Footprint** | **⚡ < 5MB Single binary** | 📦 Medium | 🐘 Heavy (PyTorch/GPU) | ☁️ Needs Database |
| **Streaming (SSE) Support** | **✅ Sub-millisecond** | ✅ Yes | ⚠️ Partial | ✅ Yes |

---

## ⚙️ Enterprise Configuration (`agentguard.yaml`)

Place an optional `agentguard.yaml` in your working directory to fine-tune guardrails:

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  target_url: "https://api.openai.com"  # or https://api.deepseek.com

circuit_breaker:
  enabled: true
  max_repeated_tool_calls: 3        # Trip breaker after 3 invariant iterations
  max_session_turns: 30             # Ceiling on conversation exchanges
  hard_budget_tokens: 150000        # Max token spend allowed per session

security:
  block_dangerous_tools: true
  blocked_patterns:
    - "rm\\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)"
    - "drop\\s+database"
    - "drop\\s+table"
    - "truncate\\s+table"
    - "chmod\\s+777"
    - "etc/passwd"
```

---

## 🧪 Live Verification & Testing

Every commit is backed by strict test coverage:

```bash
# Run automated test suite
pytest

# Run the interactive live attack & breaker demo
python examples/demo_agent.py
```

---

## 🛣️ Roadmap

- [x] Zero-code OpenAI wire protocol reverse proxy
- [x] Sliding-window canonical tool hash circuit breaker
- [x] Out-of-the-box regex & AST dangerous command interceptor
- [ ] **SSE Stream-level early abort chunk assembler**
- [ ] **Slack / Lark / Discord Human-in-the-Loop approval webhooks**
- [ ] **Lightweight Web UI Dashboard for visual incident replay**

---

## 🤝 Community & Support

Have an idea for a safety rule or edge-case loop pattern? 

- 🌟 **Star this repo** if it saved you even $1 in API bills!
- 🐛 [Open an Issue](https://github.com/cuic19053-hue/agent-guard/issues) for suggestions or bug reports.
- 💡 [Submit a Pull Request](https://github.com/cuic19053-hue/agent-guard/pulls) to contribute defense heuristics.

---

## 📄 License

AgentGuard is licensed under the [Apache 2.0 License](LICENSE).
