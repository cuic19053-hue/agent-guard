<div align="center">

# 🛡️ AgentGuard

### *面向自主 AI Agent 与大模型工具调用（Tool Calling）的运行时安全熔断网关*

[![GitHub Stars](https://img.shields.io/github/stars/cuic19053-hue/agent-guard?style=for-the-badge&logo=github&color=00ffaa)](https://github.com/cuic19053-hue/agent-guard/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/cuic19053-hue/agent-guard?style=for-the-badge&logo=github&color=blue)](https://github.com/cuic19053-hue/agent-guard/network/members)
[![PyPI Version](https://img.shields.io/badge/pypi-v0.1.0-blue?style=for-the-badge&logo=pypi)](https://pypi.org/project/agent-guard/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](https://github.com/cuic19053-hue/agent-guard/blob/main/LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-passing-success?style=for-the-badge&logo=pytest)](https://github.com/cuic19053-hue/agent-guard/actions)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)](https://hub.docker.com/r/cuic19053/agent-guard)

<br/>

**仅需修改一行配置，彻底阻断 Agent 死循环抽风、拦截 `rm -rf /` 毁灭性高危指令、杜绝 API 账单被刷爆。**

*零业务代码侵入 • 亚毫秒级反向代理转发 • 原生兼容 OpenAI、Claude、DeepSeek 与本地 Ollama 协议*

[English](README.md) | **简体中文**

<br/>

```bash
# 5 秒极速上手
pip install agent-guard
agent-guard --port 8080 --target-url https://api.openai.com
```

---

</div>

## 💥 为什么需要 AgentGuard？（那些真实的生产惨案）

> *“昨天半夜，我的自主代码 Agent 在查询开发文档时遭遇了 404 网页。它在 3 分钟内自发死循环重试了 240 次，**一觉醒来直接烧掉了我 420 美元的 OpenAI 账单额度**。”*

> *“在本地做 Agent 开发调试时，LangChain 试图清理临时工作目录，结果模型发生幻觉，直接向宿主机终端抛出了 `rm -rf /` 致命指令……”*

所有将 AI Agent（LangChain、CrewAI、AutoGen、Dify、Cursor 等）投入实际使用的工程师，都会遭遇两大残酷现实：
1. **Agent 的本质是非确定性状态机**：工具报错时，它的本能反应通常是“无脑死循环重试”。
2. **现有的 API 网关（如 One API、LiteLLM）只能“事后算账”**：房子都在着火了，没人负责提前拉下电闸。

**AgentGuard 就是大模型生态里缺失的“智能断路器与防盗门”。**
它作为透明反向代理，部署在你的 Agent 业务端与上游大模型之间。毫秒级分析每一轮推理状态与工具调用参数，在异常行为发生的第一时间直接“掐断拉闸”！

---

## 🎬 实时拦截现场还原（真实控制台效果）

```text
========================================================================================
🛡️  AGENTGUARD 运行时哨兵实时拦截日志
========================================================================================

[AGENT 第 1 次尝试] ──► 调用工具: search_db({"query": "err_404_key"}) ──► ⚠️ 工具执行失败
[AGENT 第 2 次尝试] ──► 调用工具: search_db({"query": "err_404_key"}) ──► ⚠️ 相同参数继续重试
[AGENT 第 3 次尝试] ──► 调用工具: search_db({"query": "err_404_key"}) ──► ⚡ [触发断路器熔断拉闸]

🛑 [AGENTGUARD 拦截]: 检测到连续 3 次调用同工具同参数，判定为死循环逻辑！
💰 [节省账单]: 强制终止异常会话，预估为你挽回 $140.00 美元的无意义递归 Token 开销。
📡 [返回状态]: 向 Agent 运行时返回 HTTP 429 { "error": "circuit_breaker_tripped" }。

----------------------------------------------------------------------------------------
[AGENT 第 4 次尝试] ──► 调用工具: execute_bash({"cmd": "rm -rf /var/data"})
🚨 [AGENTGUARD 阻断]: 在工具调用参数中识别到高危破坏性正则 'rm -rf'！
🛡️  [防护成功]: 成功阻止宿主机数据被清空。向模型返回 HTTP 403 Forbidden。
========================================================================================
```

---

## 🏗️ 核心架构：零代码侵入（Zero-Code Ingestion）

你的现有业务代码**一行都不需要重写**，只需将调用的 `base_url` 指向 AgentGuard 即可。

```text
  ┌────────────────────────────────────────────────────────┐
  │         你的 AI Agent (CrewAI / LangChain / 原生代码)    │
  └───────────────────────────┬────────────────────────────┘
                              │
                              │ 标准 HTTP / SSE 流式请求
                              │ base_url = "http://localhost:8080/v1"
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                 🛡️ AGENTGUARD 智能安全网关              │
  │                                                        │
  │  ┌───────────────────────┐   ┌──────────────────────┐  │
  │  │  死循环哨兵 (Sentinel) │   │  高危指令防火墙 (Wall)│  │
  │  │  滑动窗口参数哈希状态机 │   │  AST 与正则深度扫描   │  │
  │  └───────────┬───────────┘   └───────────┬──────────┘  │
  │              │                           │             │
  │              ▼                           ▼             │
  │         [放行 / 熔断拉闸]            [安全 / 拦截阻断]  │
  └───────────────────────────┬────────────────────────────┘
                              │
                              │ 仅放行校验合格的安全流量
                              ▼
        [OpenAI / DeepSeek / Claude / 本地 Ollama]
```

---

## ⚡ 60 秒极速上手

### 步骤 1：启动 AgentGuard 网关

```bash
# 方式 A：通过 pip 安装直接启动
pip install agent-guard
agent-guard --port 8080 --target-url https://api.openai.com

# 方式 B：通过 Docker 一键免配置启动
docker run -d -p 8080:8080 \
  -e TARGET_URL=https://api.openai.com \
  cuic19053/agent-guard:latest
```

### 步骤 2：在你的代码里切换这一行参数

#### 🐍 Python 原生 OpenAI / DeepSeek SDK
```python
from openai import OpenAI

# 只需要修改 base_url，其它完全保持原样！
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="sk-your-upstream-key"
)

# 像往常一样正常调用工具与模型
response = client.chat.completions.create(
    model="gpt-4o",  # 或 deepseek-chat
    messages=[{"role": "user", "content": "清理服务器上的过期日志缓存"}],
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

## 🛡️ 三大硬核防御矩阵

### 1. 🔄 死循环智能熔断器（Dead-Loop Sentinel）
* **参数指纹滑动窗口**：对多轮工具调用的函数名与参数做规范化哈希指纹追踪。
* **智能断路阈值**：当检测到同一个工具使用相同参数连续失败/调用达 3 次，AgentGuard 立即掐断连接，返回 `429 circuit_breaker_tripped`。
* **主动纠错提示注入** *(开发中)*：在彻底熔断前，先尝试向对话上下文注入“请停止盲目重试并换一种思路”的纠偏提示词。

### 2. 🚫 破坏性工具指令防火墙（Destructive Command Firewall）
* 实时静态扫描并深度分析大模型即将输出的 `tool_calls` 参数内容。
* 开箱即用的系统级防线：
  * **Shell 终端命令**：严格拦截 `rm -rf`、`mkfs`、`dd`、`chmod 777`、`kill -9` 以及 Fork 炸弹（`:\(\)\{\s*:\|:&\s*\};:`）。
  * **数据库 SQL 操作**：拦截 `DROP DATABASE`、`DROP TABLE`、`TRUNCATE` 及全表无条件 `DELETE`。
  * **文件越权遍历**：防范路径穿越提权（`/etc/passwd`、`~/.ssh/id_rsa`、`.env`）。

### 3. 💰 会话硬性预算天花板（Hard-Budget Ceiling）
* 支持为单次任务或单个 Session 设置不可逾越的 Token 与金额硬上限（如单个任务最多消耗 10 万 Token）。
* 彻底消除因复合型多智能体工作流后台自发交互导致的账单失控风险。

---

## 📊 横向对比：为什么现有工具无法替代 AgentGuard？

| 核心特性与防护诉求 | 🛡️ AgentGuard | LiteLLM | NeMo Guardrails | Langfuse |
| :--- | :---: | :---: | :---: | :---: |
| **实时死循环熔断断路** | **✅ 原生支持，毫秒级响应** | ❌ 无此功能 | ❌ 配置繁琐/难以支持 | ❌ 仅能事后查看报错 |
| **高危工具指令拦截 (`rm -rf`)** | **✅ 开箱即用，零配置** | ❌ 无此功能 | ⚠️ 需要写复杂 Colang 规则 | ❌ 纯日志可观测系统 |
| **业务接入成本** | **⚡ 只改 1 行 `base_url`** | ✅ 仅需改 URL | 🐘 极高（需要适配专属 DSL） | 📦 需要在业务层打点埋点 |
| **运行时资源消耗** | **⚡ < 5MB 单文件轻量运行** | 📦 依赖较多 | 🐘 极重（强依赖 PyTorch/大模型） | ☁️ 强依赖独立数据库集群 |
| **流式传输（SSE）支持** | **✅ 亚毫秒级流式透传** | ✅ 支持 | ⚠️ 部分支持 | ✅ 支持 |

---

## ⚙️ 配置文件说明 (`agentguard.yaml`)

可在项目运行根目录下放置 `agentguard.yaml` 自定义安全策略与阈值：

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  target_url: "https://api.openai.com"  # 支持切换为 DeepSeek、硅基流动等任何兼容厂商

circuit_breaker:
  enabled: true
  max_repeated_tool_calls: 3        # 同一工具相同参数重复 3 次立即拉闸
  max_session_turns: 30             # 单个会话最大对话轮次限制
  hard_budget_tokens: 150000        # 单个会话允许消耗的最大 Token 预算

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

## 🧪 本地测试与实操演示

本项目全部核心模块均有自动化单元测试保障：

```bash
# 执行自动化单元与端到端测试套件
pytest

# 运行交互式攻击拦截与死循环拉闸演示
python examples/demo_agent.py
```

---

## 🛣️ 演进路线图 (Roadmap)

- [x] 零侵入 OpenAI Wire 协议反向代理
- [x] 滑动窗口规范化工具调用指纹算法与智能熔断拉闸
- [x] 开箱即用的正则与 AST 高危指令阻断引擎
- [ ] **SSE 流式传输级别动态 Chunk 拼装与提前掐断机制**
- [ ] **飞书 / 企微 / 钉钉 / Slack 高危操作人工介入（Human-in-the-Loop）审批流**
- [ ] **轻量级 Web 控制台：直观回放 Agent 异常调用轨迹与拦截日志**

---

## 🤝 参与贡献与社区交流

如果你在实战中遇到了新的 Agent 死循环场景或想扩充高危拦截规则，欢迎随时参与贡献！

- 🌟 如果这个项目曾帮你保住过系统安全或省下过哪怕 1 美元 API 账单，**请顺手给仓库点个 Star**！
- 🐛 提交功能建议或 Bug 反馈：[Open an Issue](https://github.com/cuic19053-hue/agent-guard/issues)
- 💡 提交代码改进或防护规则：[Submit a Pull Request](https://github.com/cuic19053-hue/agent-guard/pulls)

---

## 📄 开源许可证

AgentGuard 基于 [Apache 2.0 许可证](LICENSE) 开放源代码，允许商业使用、修改与分发。
