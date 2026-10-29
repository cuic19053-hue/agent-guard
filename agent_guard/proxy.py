import json
import logging
from typing import AsyncGenerator
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from .config import Settings, load_settings
from .circuit_breaker import CircuitBreaker

logger = logging.getLogger("agentguard")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(
    title="AgentGuard Proxy Gateway",
    description="The Circuit Breaker & Safety Firewall for AI Agents",
    version="0.1.0"
)

settings: Settings = load_settings()
breaker = CircuitBreaker(
    max_repeated=settings.circuit_breaker.max_repeated_tool_calls,
    blocked_patterns=settings.security.blocked_patterns if settings.security.block_dangerous_tools else []
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "agent-guard",
        "circuit_breaker": settings.circuit_breaker.enabled,
        "target_url": settings.server.target_url
    }

def extract_session_id(body: dict, headers: dict) -> str:
    """Derive session ID from custom header, user message content, or client IP."""
    if "x-session-id" in headers:
        return headers["x-session-id"]
    if "user" in body:
        return str(body["user"])
    # Fallback to hashing the system message or first user message
    messages = body.get("messages", [])
    if messages:
        return str(hash(messages[0].get("content", "")))
    return "default-session"

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    target_base = settings.server.target_url.rstrip("/")
    target_endpoint = f"{target_base}/v1/chat/completions"

    raw_body = await request.body()
    try:
        body = json.loads(raw_body.decode("utf-8"))
    except Exception:
        body = {}

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)

    session_id = extract_session_id(body, headers)
    is_stream = body.get("stream", False)

    # 1. Forward request to upstream provider
    client = httpx.AsyncClient(timeout=120.0)

    if not is_stream:
        try:
            upstream_resp = await client.post(
                target_endpoint,
                headers=headers,
                content=raw_body
            )
            await client.aclose()
        except Exception as e:
            await client.aclose()
            logger.error(f"Upstream request failed: {e}")
            raise HTTPException(status_code=502, detail=f"Bad Gateway to upstream: {str(e)}")

        resp_data = upstream_resp.json()
        
        # 2. Check tool calls in response
        choices = resp_data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            tool_calls = message.get("tool_calls", [])
            for tc in tool_calls:
                func = tc.get("function", {})
                tool_name = func.get("name", "")
                args = func.get("arguments", "")

                # Check dangerous commands
                if settings.security.block_dangerous_tools:
                    is_danger, reason = breaker.check_dangerous_tool(tool_name, args)
                    if is_danger:
                        logger.warning(f"🚨 [AgentGuard Blocked High-Risk Tool] {tool_name}: {reason}")
                        return JSONResponse(
                            status_code=403,
                            content={
                                "error": {
                                    "message": f"AgentGuard Safety Violation: {reason}",
                                    "type": "dangerous_tool_blocked",
                                    "code": "tool_execution_prohibited"
                                }
                            }
                        )

                # Check infinite loops
                if settings.circuit_breaker.enabled:
                    is_tripped, count = breaker.record_and_check_loop(session_id, tool_name, args)
                    if is_tripped:
                        logger.warning(f"⚡ [AgentGuard Circuit Breaker Tripped] {tool_name} repeated {count} times!")
                        return JSONResponse(
                            status_code=429,
                            content={
                                "error": {
                                    "message": f"AgentGuard Circuit Breaker Tripped: Infinite loop detected ({tool_name} called with identical arguments {count} times). Execution halted to protect API budget.",
                                    "type": "circuit_breaker_tripped",
                                    "code": "infinite_loop_detected"
                                }
                            }
                        )

        return Response(
            content=upstream_resp.content,
            status_code=upstream_resp.status_code,
            headers=dict(upstream_resp.headers)
        )

    else:
        # Stream support
        async def stream_generator() -> AsyncGenerator[bytes, None]:
            try:
                async with client.stream("POST", target_endpoint, headers=headers, content=raw_body) as resp:
                    async for chunk in resp.aiter_bytes():
                        yield chunk
            finally:
                await client.aclose()

        return StreamingResponse(stream_generator(), media_type="text/event-stream")
