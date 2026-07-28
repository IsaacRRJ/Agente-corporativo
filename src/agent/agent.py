import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

sys.path.append(str(Path(__file__).parents[1]))
from retrieval.retriever import retrieve

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Score mínimo del reranker para intentar generar respuesta.
# Por debajo de este umbral, ningún fragmento es suficientemente relevante.
CONFIDENCE_THRESHOLD = 0.1

AREA_CONTACTS = {
    "rrhh":       "rrhh@marketnova.com",
    "financiero":  "finanzas@marketnova.com",
    "legal":       "legal@marketnova.com",
    "sistemas":    "soporte@marketnova.com",
    "operacional": "operaciones@marketnova.com",
    "marketing":   "marketing@marketnova.com",
}

SYSTEM_PROMPT = """Eres el agente corporativo de MarketNova, una asistente interna que ayuda a los colaboradores a consultar políticas, procesos y documentación de la empresa.

Reglas que debes seguir siempre:
1. Responde ÚNICAMENTE con base en el contexto de documentos proporcionado. No uses conocimiento externo.
2. Si el contexto no contiene la información necesaria para responder, dilo explícitamente.
3. Cita siempre la fuente al final de tu respuesta, indicando el nombre del archivo y la categoría.
4. Sé claro, directo y usa un tono profesional pero amigable.
5. Si la pregunta es ambigua, aclara en qué documento encontraste la información.
"""

PROMPT_TEMPLATE = """Contexto de documentos internos de MarketNova:

{context}

---

Pregunta del colaborador: {query}

Responde con base únicamente en el contexto anterior. Al final de tu respuesta incluye una sección "Fuentes:" con los archivos utilizados."""

FALLBACK_TEMPLATE = """Lo siento, no encontré información sobre eso en los documentos internos disponibles de MarketNova.

Te recomiendo contactar directamente al área responsable:
{contacts}

Si crees que este tema debería estar cubierto en la base de conocimiento, puedes reportarlo al equipo de Sistemas (soporte@marketnova.com)."""


def _build_fallback(sources: list[dict]) -> str:
    categories = {s["category"] for s in sources if s.get("category")}
    if categories:
        contacts = "\n".join(
            f"- {cat.upper()}: {AREA_CONTACTS.get(cat, 'consulta con tu líder directo')}"
            for cat in sorted(categories)
        )
    else:
        contacts = "- Recursos Humanos: rrhh@marketnova.com\n- Sistemas: soporte@marketnova.com"
    return FALLBACK_TEMPLATE.format(contacts=contacts)


def answer(query: str, category: str | None = None) -> dict:
    """
    Responde una pregunta del colaborador usando el pipeline RAG completo.

    Retorna:
      - response (str): texto de respuesta
      - sources (list): archivos utilizados
      - answered (bool): True si se encontró contexto suficiente
    """
    result = retrieve(query, category=category)
    context = result["context"]
    sources = result["sources"]
    top_score = result.get("top_score", -99.0)

    # Fallback: sin contexto o confianza insuficiente
    if not context or top_score < CONFIDENCE_THRESHOLD:
        return {
            "response": _build_fallback(sources),
            "sources": [],
            "answered": False,
        }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": PROMPT_TEMPLATE.format(context=context, query=query)},
        ],
        max_tokens=1024,
    )

    return {
        "response": response.choices[0].message.content,
        "sources": sources,
        "answered": True,
    }


if __name__ == "__main__":
    query = input("Pregunta: ")
    result = answer(query)
    print("\n" + result["response"])
    if result["sources"]:
        print("\nFuentes:")
        for s in result["sources"]:
            print(f"  - {s['filename']} ({s['category']})")
