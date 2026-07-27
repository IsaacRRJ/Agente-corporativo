import sys
from pathlib import Path
from sentence_transformers import CrossEncoder

sys.path.append(str(Path(__file__).parents[1]))
from vectorstore.store import search

# Modelo cross-encoder multilingüe para reranking
_reranker: CrossEncoder | None = None
RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def retrieve(
    query: str,
    k_candidates: int = 20,
    k_final: int = 4,
    category: str | None = None,
) -> dict:
    """
    Pipeline completo de recuperación RAG:
      1. Búsqueda semántica amplia (k_candidates fragmentos)
      2. Reranking con cross-encoder
      3. Selección de los k_final mejores
      4. Ensamblaje del contexto para el LLM

    Retorna un dict con el contexto listo y los fragmentos con sus metadatos.
    """
    # 1. Búsqueda semántica inicial
    candidates = search(query, k=k_candidates, category=category)

    if not candidates:
        return {"context": "", "sources": []}

    # 2. Reranking
    reranker = get_reranker()
    pairs = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(scores, candidates),
        key=lambda x: x[0],
        reverse=True,
    )

    # 3. Selección de los mejores
    top = [item for _, item in ranked[:k_final]]

    # 4. Ensamblaje del contexto
    context_blocks = []
    for chunk in top:
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
        for c in top
    ]

    return {"context": context, "sources": sources}
