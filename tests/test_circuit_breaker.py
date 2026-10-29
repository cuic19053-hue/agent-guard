from agent_guard.circuit_breaker import CircuitBreaker

def test_circuit_breaker_loop_detection():
    breaker = CircuitBreaker(max_repeated=3)
    session_id = "test-session-1"

    # 1st call
    tripped, count = breaker.record_and_check_loop(session_id, "fetch_url", '{"url": "http://err.com"}')
    assert not tripped
    assert count == 1

    # 2nd call with same param
    tripped, count = breaker.record_and_check_loop(session_id, "fetch_url", '{"url": "http://err.com"}')
    assert not tripped
    assert count == 2

    # 3rd call with same param -> Should Trip!
    tripped, count = breaker.record_and_check_loop(session_id, "fetch_url", '{"url": "http://err.com"}')
    assert tripped
    assert count == 3

def test_dangerous_tool_blocking():
    breaker = CircuitBreaker(blocked_patterns=[r"rm\s+-rf", r"drop\s+table"])

    # Safe call
    is_danger, _ = breaker.check_dangerous_tool("bash", 'ls -la')
    assert not is_danger

    # Dangerous rm -rf
    is_danger, reason = breaker.check_dangerous_tool("bash", 'rm -rf /')
    assert is_danger
    assert "Blocked dangerous command" in reason

    # Dangerous drop table
    is_danger, reason = breaker.check_dangerous_tool("sql_query", 'DROP TABLE users;')
    assert is_danger
    assert "Blocked dangerous command" in reason

if __name__ == "__main__":
    test_circuit_breaker_loop_detection()
    test_dangerous_tool_blocking()
    print("All unit tests passed successfully!")
