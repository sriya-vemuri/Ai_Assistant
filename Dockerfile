# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /usr/src/app

# Install OS-level deps (for FAISS, PyPDF2, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libopenblas-dev \
      libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt



# Copy the rest of the app
COPY . .

# Expose both ports
EXPOSE 8000 8501

# Default to a shell so we can override via docker-compose
CMD ["bash"]
