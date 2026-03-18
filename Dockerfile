FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_CACHE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN pip install uv

COPY pyproject.toml README.md ./
RUN uv sync

COPY src/ ./src/

RUN mkdir -p /app/storage

ENV PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "root.entrypoints.api:create_app", \
     "--factory", "--host", "0.0.0.0", "--port", "8000"]
