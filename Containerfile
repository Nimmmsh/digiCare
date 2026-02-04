# =============================================================================
# Containerfile for Patient Management System Flask App
# =============================================================================
# This is the Podman/Docker build file for the Flask application.
# We use a Python base image and install dependencies with Poetry.
#
# Build: podman build -t patient-app .
# Run:   podman run -p 5000:5000 patient-app
# =============================================================================

# Use official Python image - slim variant for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Environment variables
# - Prevents Python from writing .pyc files
# - Ensures output is sent straight to terminal (no buffering)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
# - gcc and python3-dev: needed for some Python packages
# - default-libmysqlclient-dev: needed for MySQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only dependency files first (for better caching)
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create a virtual environment
# (We're already in a container, no need for venv)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application
COPY . .

# Expose the Flask port
EXPOSE 5000

# Run the application
# Using Python directly is simpler than gunicorn for this minimal app
CMD ["python", "run.py"]

