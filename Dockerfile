FROM python:3.11-slim

WORKDIR /app

# Add app directory to PYTHONPATH
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        gcc \
        python3-dev \
        libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Configure poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --with fastapi,temporal

# Copy the rest of the application
COPY . .

# Install the package itself
RUN poetry install --only-root

# Command to run the FastAPI application
CMD ["uvicorn", "src.app.app:app", "--host", "0.0.0.0", "--port", "8000"]