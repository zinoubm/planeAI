# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install uv for parallel, ultra-fast package resolution
RUN pip install --no-cache-dir uv

COPY requirements.txt ./requirements.txt

# Cache downloaded wheels across builds so they never redownload unnecessarily
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

COPY mcp_server.py ./mcp_server.py

CMD ["python", "mcp_server.py"]