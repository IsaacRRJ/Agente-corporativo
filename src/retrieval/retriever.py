import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))
from vectorstore.store import search


def retrieve(
    query: str,
    k_final: int = 4,
    category: str | None = None,
) -> dict:
    """
    Recupera los fragmentos más relevantes usando embeddings de OpenAI.
    Retorna contexto ensamblado y metadatos de fuentes.
    """
    results = search(query, k=k_final, category=category)

    if not results:
        return {"context": "", "sources": [], "top_score": -99.0}

    # Chroma devuelve distancia (menor = más relevante); convertimos a score
    top_score = 1 - results[0]["score"] if results else -99.0

    context_blocks = []
    for chunk in results:
        meta = chunk["metadata"]
        header = f"[{meta.get('category', '').upper()} | {meta.get('filename', '')}]"
        context_blocks.append(f"{header}\n{chunk['text']}")

    context = "\n\n---\n\n".join(context_blocks)

    sources = [
        {
            "filename": c["metadata"].get("filename"),
            "category": c["metadata"].get("category"),
            "filepath": c["metadata"].get("filepath"),
        }
        for c in results
    ]

    return {"context": context, "sources": sources, "top_score": top_score}
