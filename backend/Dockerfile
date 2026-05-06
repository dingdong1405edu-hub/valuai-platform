# ── Stage 1: System dependencies (WeasyPrint needs native libs) ──────────────
FROM python:3.11-slim AS system-deps

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    libcairo2 \
    libgdk-pixbuf-xlib-2.0-0 \
    libglib2.0-0 \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    libpng-dev \
    shared-mime-info \
    fontconfig \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# ── Stage 2: Python dependencies ─────────────────────────────────────────────
FROM system-deps AS python-deps

WORKDIR /install

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 3: Final image ──────────────────────────────────────────────────────
FROM system-deps AS final

WORKDIR /app

# Copy installed Python packages from python-deps stage
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy application source
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
