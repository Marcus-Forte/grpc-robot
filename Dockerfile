# Build the server
FROM ghcr.io/astral-sh/uv:trixie-slim

COPY . /app

WORKDIR /app

RUN uv sync

CMD ["uv", "run", "--", "python", "-m", "app.server"]