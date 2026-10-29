FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY agent_guard/ ./agent_guard/
COPY agentguard.yaml ./

RUN pip install --no-cache-dir .

EXPOSE 8080

ENTRYPOINT ["agent-guard"]
CMD ["--host", "0.0.0.0", "--port", "8080"]
