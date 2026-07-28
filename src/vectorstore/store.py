import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CHROMA_DIR = Path(__file__).parents[2] / "chroma_db"
COLLECTION_NAME = "marketnova_docs"

_vectorstore: Chroma | None = None


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.environ["OPENAI_API_KEY"],
        )
        _vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR),
        )
    return _vectorstore


def search(query: str, k: int = 4, category: str | None = None) -> list[dict]:
    """
    Busca los k fragmentos más relevantes para la consulta.
    Si se especifica category, filtra por esa categoría antes de calcular similitud.
    """
    store = get_vectorstore()
    filter_dict = {"category": category} if category else None

    results = store.similarity_search_with_score(query, k=k, filter=filter_dict)

    return [
        {
            "text": doc.page_content,
            "score": round(float(score), 4),
            "metadata": doc.metadata,
        }
        for doc, score in results
    ]


def available_categories() -> list[str]:
    """Devuelve las categorías únicas almacenadas en la base vectorial."""
    store = get_vectorstore()
    collection = store._collection
    all_meta = collection.get(include=["metadatas"])["metadatas"]
    return sorted({m["category"] for m in all_meta if "category" in m})
