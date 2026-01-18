# Build the server
FROM ghcr.io/astral-sh/uv:trixie-slim

# ENV DEBIAN_FRONTEND=noninteractive
# ENV PATH="/root/.local/bin:$PATH"
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV GPIOZERO_PIN_FACTORY=lgpio

# This will install gpiozero and some other dependencies to allow use of GPIO pins on a Raspberry Pi
RUN apt-get update && apt-get install -y \
    swig gcc wget curl python3-pip python3-setuptools python3-dev unzip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install lgpio
RUN cd /tmp && wget http://abyz.me.uk/lg/lg.zip && \
    unzip lg.zip && cd lg && \
    make install && \
    rm -r /tmp/lg*

# TODO copy libraries only, not build tools.

COPY . /app

WORKDIR /app

# lgpio only present in devcontainer
RUN uv add lgpio && uv sync

CMD ["python", "-m", "app.server"]