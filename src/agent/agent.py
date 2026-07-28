import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

sys.path.append(str(Path(__file__).parents[1]))
from retrieval.retriever import retrieve

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Distancia L2 máxima aceptable (menor = más similar).
# Basado en datos reales: contenido relevante ≤ 1.3, irrelevante ≥ 1.4.
MAX_DISTANCE = 1.3

# Mensajes conversacionales que no deben pasar por el pipeline RAG
_CONVERSATIONAL_RE = re.compile(
    r"^\s*(hola|buenas?|buenos\s+d[ií]as?|buenas?\s+tardes?|buenas?\s+noches?|"
    r"hi|hello|hey|gracias?|thank|de\s+nada|ok|okay|perfecto|genial|entendido|"
    r"listo|bien|claro|nos\s+vemos|hasta\s+luego|adi[oó]s|chao|bye|"
    r"qu[eé]\s+tal|c[oó]mo\s+est[aá]s?|c[oó]mo\s+andas?|"
    r"qu[eé]\s+puedes\s+hacer|para\s+qu[eé]\s+sirves|"
    r"ayúdame|ayudame|necesito\s+ayuda|puedes\s+ayudarme)\s*[!?.]*\s*$",
    re.IGNORECASE,
)

AREA_CONTACTS = {
    "rrhh":        "rrhh@marketnova.com",
    "financiero":  "finanzas@marketnova.com",
    "legal":       "legal@marketnova.com",
    "sistemas":    "soporte@marketnova.com",
    "operacional": "operaciones@marketnova.com",
    "marketing":   "marketing@marketnova.com",
}

# --- Prompts para respuestas con contexto RAG ---

RAG_SYSTEM = """Eres el agente corporativo de MarketNova, una asistente interna que ayuda a los colaboradores a consultar políticas, procesos y documentación de la empresa.

Reglas:
1. Responde ÚNICAMENTE con base en el contexto de documentos proporcionado. No uses conocimiento externo.
2. Si el contexto no contiene la información necesaria, dilo explícitamente.
3. Cita siempre la fuente al final de tu respuesta, indicando el nombre del archivo y la categoría.
4. Sé claro, directo y usa un tono profesional pero amigable.
5. Si la pregunta es ambigua, aclara en qué documento encontraste la información."""

RAG_PROMPT = """Contexto de documentos internos de MarketNova:

{context}

---

Pregunta del colaborador: {query}

Responde con base únicamente en el contexto anterior. Sé claro y directo. No incluyas una sección de fuentes al final."""


# --- Prompts para saludos y preguntas sin contexto ---

CONVERSATIONAL_SYSTEM = """Eres el agente corporativo de MarketNova, una asistente interna amigable y profesional.

Tu función principal es ayudar a los colaboradores a consultar documentos internos en estas áreas:
- RRHH: vacaciones, beneficios, onboarding (rrhh@marketnova.com)
- Financiero: gastos, reembolsos (finanzas@marketnova.com)
- Legal: privacidad, compliance (legal@marketnova.com)
- Sistemas: APIs, soporte técnico (soporte@marketnova.com)
- Operacional: devoluciones, envíos (operaciones@marketnova.com)
- Marketing: catálogo, precios (marketing@marketnova.com)

Comportamiento según el tipo de mensaje:
- Saludo, agradecimiento o comentario casual → responde con calidez y brevedad, invita al colaborador a hacer preguntas sobre los documentos.
- Pregunta sobre la empresa sin información disponible → explícalo claramente y sugiere el contacto del área responsable.
- Nunca inventes información que no provenga de los documentos internos."""

CONVERSATIONAL_PROMPT = """El colaborador envió este mensaje: "{query}"

No encontré documentos internos relevantes para esta consulta.

Responde de forma apropiada:
- Saludo o mensaje casual → responde con calidez y guíalo a hacer preguntas sobre los documentos.
- Pregunta sin información disponible → indica que no encontraste la información y sugiere el área de contacto más apropiada."""


def answer(query: str, category: str | None = None) -> dict:
    # Mensajes conversacionales: omitir RAG por completo
    if _CONVERSATIONAL_RE.match(query.strip()):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": CONVERSATIONAL_SYSTEM},
                {"role": "user",   "content": CONVERSATIONAL_PROMPT.format(query=query)},
            ],
            max_tokens=250,
        )
        return {"response": resp.choices[0].message.content, "sources": [], "answered": False}

    result = retrieve(query, category=category)
    context   = result["context"]
    sources   = result["sources"]
    top_score = result.get("top_score", 99.0)

    # Sin contexto relevante → respuesta conversacional / fallback vía LLM
    if not context or top_score > MAX_DISTANCE:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": CONVERSATIONAL_SYSTEM},
                {"role": "user",   "content": CONVERSATIONAL_PROMPT.format(query=query)},
            ],
            max_tokens=350,
        )
        return {
            "response": resp.choices[0].message.content,
            "sources": [],
            "answered": False,
        }

    # Respuesta RAG con contexto de documentos
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": RAG_SYSTEM},
            {"role": "user",   "content": RAG_PROMPT.format(context=context, query=query)},
        ],
        max_tokens=1024,
    )

    return {
        "response": _clean_response(resp.choices[0].message.content),
        "sources": sources,
        "answered": True,
    }


def _clean_response(text: str) -> str:
    """Elimina cualquier sección 'Fuentes:' que el LLM genere en el texto."""
    return re.sub(
        r"\n+\*{0,2}fuentes?\*{0,2}:.*$",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    ).strip()


if __name__ == "__main__":
    query = input("Pregunta: ")
    result = answer(query)
    print("\n" + result["response"])
    if result["sources"]:
        print("\nFuentes:")
        for s in result["sources"]:
            print(f"  - {s['filename']} ({s['category']})")
