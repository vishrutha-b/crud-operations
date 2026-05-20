# ── Stage 1: Build ───────────────────────────────────────────
FROM python:3.9-slim AS builder

WORKDIR /app

# Install system dependencies for building (e.g., gcc for psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a specific folder to copy later
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.9-slim AS runtime

WORKDIR /app

# Install only the runtime library for PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the installed packages from the builder stage
COPY --from=builder /root/.local /root/.local
# Copy the application source
COPY . .

# Ensure the local bin folder is in the PATH
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
