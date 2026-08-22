FROM python:3.11-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase and model artifacts
COPY . .

# Set Cloud Run Environment Port (defaults to 8080)
ENV PORT=8080
EXPOSE 8080

# Healthcheck endpoint
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Start Streamlit application
ENTRYPOINT ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false"]
