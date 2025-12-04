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

RUN pip install -r requirements.txt; 

COPY . /core
