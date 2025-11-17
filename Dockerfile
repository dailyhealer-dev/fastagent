# Base Python image
FROM python:3.13.7-bookworm

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy uv binaries from GHCR
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Streamlit entrypoint
CMD ["streamlit", "run", "index.py", "--server.port=8501", "--server.address=0.0.0.0"]
