# /services/document-processor/Dockerfile
FROM python:3.12-slim AS base

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src
ENV PROJECT_BASE_PATH=/app

WORKDIR /app

# Install system dependencies for python-docx
RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

COPY --chown=processor:processor pyproject.toml poetry.lock* ./
# Install dependencies (without virtualenv) # Install Poetry
RUN pip install --upgrade pip \
  && pip install --no-cache-dir poetry \
  && pip install uvicorn fastapi \
  && poetry config virtualenvs.create false

RUN poetry install --no-root

COPY src /app


EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--reload","--host", "0.0.0.0", "--port", "8000"]
