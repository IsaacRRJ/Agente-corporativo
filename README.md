# Agente Corporativo IA — MarketNova

> Agente de inteligencia artificial corporativo para colaboradores de **MarketNova**, un e-commerce latinoamericano de productos del hogar y tecnología. El agente responde preguntas basadas en documentos internos de la empresa de forma conversacional, centralizada y siempre disponible — con acceso restringido solo a empleados verificados.

---

## Demo

https://agente-corporativo-p10h.onrender.com/


---

## Descripción

**MarketNova** es una empresa hipotética de e-commerce con operaciones en Latinoamérica. Este agente RAG (_Retrieval-Augmented Generation_) permite a cualquier colaborador consultar documentos internos sin necesidad de buscar manualmente en carpetas o contactar a otras áreas.

El sistema incluye autenticación por código de empleado, lo que garantiza que solo el personal de la empresa pueda acceder a la información interna.

**Ejemplos de preguntas que puede responder:**
- _"¿Cuántos días de vacaciones tengo en mi primer año?"_
- _"¿Cuál es el proceso para gestionar una devolución de cliente?"_
- _"¿Cuál es la política de reembolso de gastos de viaje?"_
- _"¿Cómo funciona la API de inventario interna?"_
- _"¿Cuál es el precio de la Laptop Lenovo IdeaPad 15?"_

---

## Arquitectura

```
agente-corporativo/
├── docs/                        # Documentos internos de MarketNova
│   ├── rrhh/                    # Políticas, onboarding, beneficios
│   ├── operacional/             # Procesos, devoluciones, envíos
│   ├── financiero/              # Gastos, reportes
│   ├── legal/                   # Términos, privacidad
│   ├── marketing/               # Catálogo, precios
│   └── sistemas/                # APIs, bases de datos
├── src/
│   ├── auth/                    # Autenticación por código de empleado
│   │   ├── auth.py              # Login, sesiones, logout
│   │   └── employees.json       # Registro de empleados autorizados
│   ├── ingestion/               # Carga y procesamiento de documentos
│   ├── vectorstore/             # ChromaDB: almacenamiento de embeddings
│   ├── retrieval/               # Búsqueda semántica por similitud
│   ├── agent/                   # Lógica del agente RAG
│   └── api/                     # API REST con FastAPI
├── frontend/                    # Interfaz web
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| **Lenguaje** | Python 3.11+ |
| **LLM** | OpenAI GPT-4o-mini |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Orquestación RAG** | LangChain |
| **Vector store** | ChromaDB |
| **API** | FastAPI |
| **Frontend** | HTML + JavaScript (sin frameworks) |
| **Contenedor** | Docker |
| **Cloud** | Oracle Cloud Infrastructure (OCI) / Render |

---

## Autenticación de empleados

El acceso al agente está restringido a colaboradores verificados de MarketNova. El sistema utiliza **códigos de empleado** con el formato `MN-XXXXX`.

### Cómo funciona

1. El colaborador ingresa su código de empleado en la pantalla de login (ej. `MN-JRUIZ`)
2. El backend valida el código contra el registro de empleados (`src/auth/employees.json`)
3. Si es válido, se genera un token de sesión y se concede acceso
4. Todos los endpoints protegidos (`/ask`, `/feedback`) requieren el token en cada solicitud
5. El token se invalida al cerrar sesión o al reiniciar el servidor

### Formato del código

```
MN-XXXXX
│   └── Identificador personal (2–8 caracteres alfanuméricos)
└── Prefijo MarketNova
```

**Ejemplos:** `MN-JRUIZ`, `MN-MLOPEZ`, `MN-IT001`

### Gestión de empleados

Los empleados autorizados se definen en `src/auth/employees.json`:

```json
{
  "employees": [
    {"code": "MN-JRUIZ",  "name": "Juan Ruiz",    "area": "Sistemas"},
    {"code": "MN-MLOPEZ", "name": "María López",  "area": "RRHH"}
  ]
}
```

Para agregar un nuevo empleado, añade una entrada al JSON y reinicia el servidor. Para revocar acceso, elimina la entrada.

---

## Funcionalidades

- **Acceso restringido** — solo empleados con código válido pueden usar el agente
- **Filtros por área** — busca en toda la base o filtra por RRHH, Financiero, Legal, Sistemas, Operacional o Marketing
- **Respuestas conversacionales** — responde saludos y mensajes casuales, no solo preguntas
- **Fuentes citadas** — muestra qué documentos respaldan cada respuesta
- **Feedback** — botones de 👍/👎 por respuesta, registrados con el código del empleado
- **Ingesta incremental** — detecta documentos nuevos o modificados y reindexea solo los cambios

---

## Formatos de documento soportados

| Formato | Extensión |
|---|---|
| PDF | `.pdf` |
| Word | `.docx` |
| Excel | `.xlsx` |
| Markdown | `.md` |
| CSV | `.csv` |
| JSON | `.json` |
| HTML | `.html` |

---

## Instalación local

### Requisitos previos
- Python 3.11+
- Clave de API de OpenAI

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/IsaacRRJ/Agente-corporativo.git
cd Agente-corporativo

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY

# 5. Indexar documentos
python src/ingestion/ingest.py

# 6. Iniciar el servidor
iniciar_servidor.bat           # Windows
# uvicorn src.api.main:app --reload --port 8000  # Mac/Linux
```

Abre tu navegador en `http://localhost:8000` e ingresa con un código de empleado (ej. `MN-DEMO01`).

---

## Endpoints de la API

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| `POST` | `/login` | No | Valida código de empleado y retorna token |
| `POST` | `/logout` | Sí | Invalida el token de sesión |
| `GET` | `/me` | Sí | Retorna datos del empleado autenticado |
| `POST` | `/ask` | Sí | Consulta al agente RAG |
| `POST` | `/feedback` | Sí | Registra feedback de una respuesta |
| `GET` | `/health` | No | Estado del servidor |

---



---

## Autor

Desarrollado por Isaac Ruiz como parte del desafío **Alura Agentes**.

---
