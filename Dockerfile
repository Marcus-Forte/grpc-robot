# Build the server
FROM ghcr.io/astral-sh/uv:bookworm-slim

ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# This will install gpiozero and some other dependencies to allow use of GPIO pins on a Raspberry Pi
RUN apt-get update && apt-get install -y \
    swig gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app

WORKDIR /app

RUN uv sync

CMD ["python", "-m", "app.server"]