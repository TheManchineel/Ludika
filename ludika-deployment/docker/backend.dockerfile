FROM python:3.13.6-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.6 /uv /uvx /bin/
# Maximize cache use by copying the uv.lock file first
COPY ludika-backend/pyproject.toml ludika-backend/uv.lock /app/
WORKDIR /app
RUN uv sync --frozen --no-cache --compile-bytecode --no-install-project

# Copy the actual application code
COPY ludika-backend/ludika_backend /app/

EXPOSE 8000
USER 99:100

CMD ["fastapi", "run", "./ludika_backend/api.py", "--host", "0.0.0.0", "--port", "8000"]