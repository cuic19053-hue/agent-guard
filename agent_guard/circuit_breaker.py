import hashlib
import json
import re
from typing import Dict, List, Optional, Tuple

class CircuitBreaker:
    def __init__(self, max_repeated: int = 3, blocked_patterns: Optional[List[str]] = None):
        self.max_repeated = max_repeated
        self.blocked_patterns = [re.compile(p, re.IGNORECASE) for p in (blocked_patterns or [])]
        # session_id -> list of tool call hashes
        self.session_history: Dict[str, List[str]] = {}

    def get_tool_call_hash(self, tool_name: str, arguments: str) -> str:
        """Normalized hash of tool name and parameters."""
        try:
            # parse JSON to normalize keys order
            parsed = json.loads(arguments)
            norm_args = json.dumps(parsed, sort_keys=True)
        except Exception:
            norm_args = arguments.strip()
        
        raw = f"{tool_name}:{norm_args}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def check_dangerous_tool(self, tool_name: str, arguments: str) -> Tuple[bool, Optional[str]]:
        """Check if arguments contain dangerous patterns (e.g. rm -rf, drop table)."""
        for pattern in self.blocked_patterns:
            if pattern.search(arguments):
                return True, f"Blocked dangerous command matching pattern: {pattern.pattern}"
        return False, None

    def record_and_check_loop(self, session_id: str, tool_name: str, arguments: str) -> Tuple[bool, int]:
        """Record tool call and detect infinite loops. Returns (is_tripped, repeat_count)."""
        call_hash = self.get_tool_call_hash(tool_name, arguments)
        history = self.session_history.setdefault(session_id, [])
        history.append(call_hash)

        # Count how many times the trailing calls are identical
        repeat_count = 0
        for h in reversed(history):
            if h == call_hash:
                repeat_count += 1
            else:
                break

        is_tripped = repeat_count >= self.max_repeated
        return is_tripped, repeat_count

    def reset_session(self, session_id: str):
        if session_id in self.session_history:
            del self.session_history[session_id]
