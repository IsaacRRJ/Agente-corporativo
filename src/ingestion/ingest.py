import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

sys.path.append(str(Path(__file__).parents[1]))
from vectorstore.store import get_vectorstore

from extractor import extract, SUPPORTED_EXTENSIONS
from cleaner import clean

load_dotenv()

DOCS_DIR = Path(__file__).parents[2] / "docs"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def get_category(path: Path) -> str:
    parts = path.relative_to(DOCS_DIR).parts
    return parts[0] if parts else "general"


def ingest():
    print("Cargando modelo de embeddings...")
    vectorstore = get_vectorstore()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    files = [
        f for f in DOCS_DIR.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    print(f"\nDocumentos encontrados: {len(files)}\n")

    for file in files:
        print(f"Procesando: {file.name}")
        raw = extract(file)
        if not raw:
            print(f"  Sin contenido extraible, saltando.\n")
            continue

        cleaned = clean(raw)
        chunks = splitter.split_text(cleaned)

        metadata = {
            "category": get_category(file),
            "filename": file.name,
            "filepath": str(file.relative_to(DOCS_DIR)),
        }

        vectorstore.add_texts(texts=chunks, metadatas=[metadata] * len(chunks))
        print(f"  {len(chunks)} fragmentos indexados.\n")

    print("Ingesta completada. Base vectorial lista en chroma_db/")


if __name__ == "__main__":
    ingest()
