FROM python:3.13.6-slim

USER 99:100
COPY --from=ghcr.io/astral-sh/uv:0.8.6 /uv /uvx /bin/
# Maximize cache by copying the uv.lock file first
COPY ludika-backend/pyproject.toml /app/
WORKDIR /app
RUN uv sync --frozen --no-cache --compile-bytecode

# Copy the actual application code
COPY ludika-backend/ludika_backend /app/
EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "ludika_backend.api:app", "--host", "::1", "--port", "8000", "--log-level", "warning"]