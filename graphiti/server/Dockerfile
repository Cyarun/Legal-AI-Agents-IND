FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy server files
COPY . .

# Install dependencies
RUN pip install uv && \
    uv pip install --system -r pyproject.toml

# Expose port
EXPOSE 8001

# Run the server
CMD ["uvicorn", "graph_service.main:app", "--host", "0.0.0.0", "--port", "8001"]