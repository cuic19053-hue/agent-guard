import os
from typing import List, Optional
from pydantic import BaseModel
import yaml

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    target_url: str = os.getenv("TARGET_URL", "https://api.openai.com")

class CircuitBreakerConfig(BaseModel):
    enabled: bool = True
    max_repeated_tool_calls: int = 3
    max_session_turns: int = 30
    hard_budget_tokens: int = 150000

class SecurityConfig(BaseModel):
    block_dangerous_tools: bool = True
    blocked_patterns: List[str] = [
        r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)", # rm -rf, rm -fr
        r"drop\s+database",
        r"drop\s+table",
        r"truncate\s+table",
        r":\(\)\{\s*:\|:&\s*\};:", # fork bomb
        r"mkfs",
        r"chmod\s+777",
        r">\s*/dev/sd[a-z]",
    ]

class Settings(BaseModel):
    server: ServerConfig = ServerConfig()
    circuit_breaker: CircuitBreakerConfig = CircuitBreakerConfig()
    security: SecurityConfig = SecurityConfig()

def load_settings(config_path: Optional[str] = None) -> Settings:
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return Settings(**data)
    elif os.path.exists("agentguard.yaml"):
        with open("agentguard.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return Settings(**data)
    return Settings()
