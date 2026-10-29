import argparse
import uvicorn
import os

def main():
    parser = argparse.ArgumentParser(description="AgentGuard: The Circuit Breaker & Safety Firewall for AI Agents")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen (default: 8080)")
    parser.add_argument("--target-url", default=None, help="Target upstream API URL (default: https://api.openai.com)")
    parser.add_argument("--config", default=None, help="Path to agentguard.yaml")

    args = parser.parse_args()

    if args.target_url:
        os.environ["TARGET_URL"] = args.target_url

    print("\n" + "="*60)
    print("🛡️  Starting AgentGuard Gateway...")
    print(f"👉 Listening on: http://{args.host}:{args.port}")
    print(f"👉 Upstream Target: {os.environ.get('TARGET_URL', 'https://api.openai.com')}")
    print("👉 Point your Agent's base_url to: http://localhost:" + str(args.port) + "/v1")
    print("="*60 + "\n")

    uvicorn.run("agent_guard.proxy:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()
