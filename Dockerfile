FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para pdfplumber y sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente y documentos
COPY src/ ./src/
COPY docs/ ./docs/
COPY frontend/ ./frontend/

# Directorio persistente para ChromaDB (se monta como volumen en producción)
RUN mkdir -p /app/chroma_db /app/logs

ENV PYTHONPATH=src

EXPOSE 8000

# Ingestar documentos y levantar el servidor
CMD ["sh", "-c", "python src/ingestion/ingest.py && uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]
