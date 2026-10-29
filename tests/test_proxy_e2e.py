import pytest
from fastapi.testclient import TestClient
from agent_guard.proxy import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "agent-guard"

def test_circuit_breaker_and_danger_interception_logic():
    from agent_guard.circuit_breaker import CircuitBreaker
    breaker = CircuitBreaker(max_repeated=3, blocked_patterns=[r"rm\s+-rf"])
    
    # Check rm -rf
    is_danger, reason = breaker.check_dangerous_tool("bash", '{"command": "rm -rf /"}')
    assert is_danger
    assert "Blocked dangerous command" in reason

    # Check safe command
    is_danger, _ = breaker.check_dangerous_tool("bash", '{"command": "git status"}')
    assert not is_danger
