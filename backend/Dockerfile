# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create and activate virtual environment
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy the entire project structure
COPY . .

# Install dependencies using uv
RUN uv pip install .

# Set environment variables
ENV PYTHONPATH=/app
ENV stage=prod
ENV POSTGRES_HOST=db
ENV POSTGRES_PORT=5432

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "backend.scripts.start_prod"]
