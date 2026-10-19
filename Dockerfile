FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    GARMINTOKENS=/tokens DATA_DIR=/data HISTORY_PATH=/data/history.jsonl \
    GOALS_PATH=/app/config/goals.yaml MCP_HOST=0.0.0.0 MCP_PORT=8000

WORKDIR /app
COPY pyproject.toml README.md ./
COPY wearable_mcp ./wearable_mcp
RUN pip install .
COPY config ./config

EXPOSE 8000
CMD ["wearable-mcp"]
