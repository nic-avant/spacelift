FROM python:3.11-slim

WORKDIR /app

# Add app directory to PYTHONPATH
ENV PYTHONPATH=/app

# Install dependencies
COPY fastapi-requirements.txt .
RUN pip install -r fastapi-requirements.txt

# Copy the rest of the application
COPY . .

RUN pip install -e .

# Command to run the FastAPI application
CMD ["uvicorn", "src.spacelift.app:app", "--host", "0.0.0.0", "--port", "8000"]