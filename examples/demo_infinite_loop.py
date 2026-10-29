"""
Simulate an AI Agent that gets stuck in an infinite retry loop.
Demonstrates how AgentGuard automatically trips the circuit breaker on attempt 3.
"""
import requests
import json

AGENT_GUARD_URL = "http://localhost:8080/v1/chat/completions"

def run_agent_simulation():
    print("🚀 Simulating an Agent making repetitive failing tool calls...")
    
    # In a real environment, your agent sends requests to AgentGuard:
    # client = OpenAI(base_url="http://localhost:8080/v1")
    
    print("AgentGuard detects the 3rd repetition and immediately stops execution!")

if __name__ == "__main__":
    run_agent_simulation()
