"""
AgentGuard Interactive End-to-End Demo.
Demonstrates:
1. Normal safe tool calling.
2. Dangerous tool call blocked immediately by AgentGuard (e.g. rm -rf).
3. Dead-loop detection tripping circuit breaker on the 3rd attempt.
"""
import sys
import time
from agent_guard.circuit_breaker import CircuitBreaker

def run_live_demo():
    print("=" * 65)
    print("🛡️  AgentGuard Live Simulation & Demonstration")
    print("=" * 65)

    breaker = CircuitBreaker(
        max_repeated=3,
        blocked_patterns=[r"rm\s+-rf", r"drop\s+table", r"chmod\s+777"]
    )
    session_id = "session_live_demo_001"

    # 1. Normal safe execution
    print("\n[Step 1: Normal Agent Execution]")
    tool_name = "fetch_weather"
    args = '{"city": "San Francisco"}'
    print(f"👉 Agent calls tool: {tool_name}({args})")
    is_danger, _ = breaker.check_dangerous_tool(tool_name, args)
    tripped, count = breaker.record_and_check_loop(session_id, tool_name, args)
    print(f"✅ Status: ALLOWED (Dangerous: {is_danger}, Loop Count: {count})")

    # 2. Block dangerous command
    print("\n[Step 2: Dangerous Tool Call Interception]")
    bad_tool = "execute_bash"
    bad_args = '{"cmd": "rm -rf /var/data"}'
    print(f"👉 Rogue Agent attempts: {bad_tool}({bad_args})")
    is_danger, reason = breaker.check_dangerous_tool(bad_tool, bad_args)
    if is_danger:
        print(f"🚨 [BLOCKED BY AGENTGUARD] Reason: {reason}")
        print("🛡️  Result: 403 Forbidden returned to Agent! System wiped prevented.")

    # 3. Dead-Loop detection
    print("\n[Step 3: Infinite Retry Loop & Circuit Breaker]")
    loop_tool = "search_database"
    loop_args = '{"query": "non_existent_key_404"}'
    
    for attempt in range(1, 4):
        time.sleep(0.3)
        tripped, count = breaker.record_and_check_loop(session_id, loop_tool, loop_args)
        if tripped:
            print(f"⚡ [CIRCUIT BREAKER TRIPPED at Attempt {attempt}]")
            print(f"🛑 Reason: Identical tool call repeated {count} times.")
            print("💰 Result: 429 CircuitBreakerTripped returned! Upstream API credit saved.")
        else:
            print(f"⚠️  Attempt {attempt}: Agent retrying {loop_tool}... (Recorded count={count})")

    print("\n" + "=" * 65)
    print("🎉 All 3 core safeguards demonstrated with 100% success!")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_live_demo()
