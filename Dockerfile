FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies first to leverage layer cache
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend_service code
COPY backend_service /app/backend_service
COPY alembic /app/alembic
COPY scripts /app/scripts

# Create non-root user
RUN groupadd -r gramsight && useradd -r -g gramsight gramsight
RUN chown -R gramsight:gramsight /app
USER gramsight

EXPOSE 8000

# Default to uvicorn serving the backend_service package
CMD ["uvicorn", "backend_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
