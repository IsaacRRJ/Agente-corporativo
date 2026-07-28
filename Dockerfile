FROM python:3.11-slim

WORKDIR /app

# Dependencias mínimas del sistema para pdfplumber
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente y documentos
COPY src/ ./src/
COPY docs/ ./docs/
COPY frontend/ ./frontend/

RUN mkdir -p /app/chroma_db /app/logs

ENV PYTHONPATH=src

EXPOSE 8000

# Indexar documentos y levantar el servidor (PORT lo asigna la plataforma)
CMD ["sh", "-c", "python src/ingestion/ingest.py && uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
