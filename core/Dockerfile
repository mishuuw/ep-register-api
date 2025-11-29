# syntax directive enables BuildKit features (cache mounts)
# Ensure Docker builds use BuildKit for cache mounts when desired
FROM python:3.12.8-slim-bookworm

WORKDIR /core

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libssl-dev \
    libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /core

# Build-time flag: set PIP_NO_CACHE=1 for production builds to disable pip cache
ARG PIP_NO_CACHE=0

# Use a cache mount for pip when available (BuildKit). If PIP_NO_CACHE=1, pip is run
# with --no-cache-dir so the cache mount is ignored.
RUN --mount=type=cache,target=/root/.cache/pip \
    if [ "${PIP_NO_CACHE}" = "1" ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    else \
        pip install -r requirements.txt; \
    fi

COPY . /core
