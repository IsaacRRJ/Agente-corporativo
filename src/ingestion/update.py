"""
Actualización incremental del índice vectorial.
Detecta archivos nuevos o modificados en docs/ y los reingesta,
eliminando primero los fragmentos anteriores del mismo archivo.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter

sys.path.append(str(Path(__file__).parents[1]))
from vectorstore.store import get_vectorstore

from extractor import extract, SUPPORTED_EXTENSIONS
from cleaner import clean

DOCS_DIR = Path(__file__).parents[2] / "docs"
STATE_FILE = Path(__file__).parents[2] / "logs" / "ingest_state.json"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def get_category(path: Path) -> str:
    parts = path.relative_to(DOCS_DIR).parts
    return parts[0] if parts else "general"


def delete_file_chunks(vectorstore, filepath: str):
    collection = vectorstore._collection
    results = collection.get(where={"filepath": filepath})
    ids = results.get("ids", [])
    if ids:
        collection.delete(ids=ids)


def process_file(path: Path, vectorstore, splitter) -> int:
    raw = extract(path)
    if not raw:
        return 0

    cleaned = clean(raw)
    chunks = splitter.split_text(cleaned)
    filepath = str(path.relative_to(DOCS_DIR))

    metadata = {
        "category": get_category(path),
        "filename": path.name,
        "filepath": filepath,
    }

    delete_file_chunks(vectorstore, filepath)
    vectorstore.add_texts(texts=chunks, metadatas=[metadata] * len(chunks))
    return len(chunks)


def update():
    state = load_state()
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

    updated = 0
    for file in files:
        key = str(file.relative_to(DOCS_DIR))
        mtime = file.stat().st_mtime

        if state.get(key) == mtime:
            continue  # sin cambios

        print(f"Actualizando: {file.name}...")
        chunks = process_file(file, vectorstore, splitter)
        state[key] = mtime
        print(f"  {chunks} fragmentos indexados.")
        updated += 1

    save_state(state)

    if updated == 0:
        print("Todo actualizado. No hay cambios.")
    else:
        print(f"\n{updated} archivo(s) actualizados en {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")


if __name__ == "__main__":
    update()
