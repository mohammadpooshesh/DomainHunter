# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# System dependencies for lxml, cryptography, whois and Playwright/Chromium.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    whois \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install the Chromium browser used by the screenshots module.
RUN playwright install --with-deps chromium

COPY . .

# Run as a non-root user.
RUN useradd --create-home --uid 10001 hunter \
    && mkdir -p /app/output /app/cache /ms-playwright \
    && chown -R hunter:hunter /app /ms-playwright
USER hunter

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
