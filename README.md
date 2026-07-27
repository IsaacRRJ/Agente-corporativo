# 🛒 MarketNova — Agente Corporativo IA

> Agente de inteligencia artificial corporativo para colaboradores de **MarketNova**, un e-commerce latinoamericano de productos del hogar y tecnología. El agente responde preguntas basadas en documentos internos de la empresa de forma conversacional, centralizada y siempre disponible.

---

## 📸 Demo

> _Captura o video del agente en producción (se agregará tras el deploy en OCI)_

---

## 🎯 Descripción

**MarketNova** es una empresa hipotética de e-commerce con operaciones en Latinoamérica. Este agente RAG (_Retrieval-Augmented Generation_) permite a cualquier colaborador consultar documentos internos sin necesidad de buscar manualmente en carpetas o contactar a otras áreas.

**Ejemplos de preguntas que puede responder:**
- _"¿Cuántos días de vacaciones tengo en mi primer año?"_
- _"¿Cuál es el proceso para gestionar una devolución de cliente?"_
- _"¿Cuál es la política de reembolso de gastos de viaje?"_
- _"¿Cómo funciona la API de inventario interna?"_
- _"¿Cuáles son los descuentos vigentes para el catálogo de tecnología?"_

---

## 🏗️ Arquitectura

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
│   ├── ingestion/               # Carga y procesamiento de documentos
│   ├── agent/                   # Lógica del agente RAG
│   └── api/                     # API REST con FastAPI
├── frontend/                    # Interfaz web simple
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🧠 Stack tecnológico

| Componente | Tecnología |
|---|---|
| **Lenguaje** | Python 3.11+ |
| **Orquestación RAG** | LangChain |
| **Modelo de lenguaje** | Claude (Anthropic API) |
| **Vector store** | ChromaDB |
| **API** | FastAPI |
| **Frontend** | HTML + JavaScript |
| **Contenedor** | Docker |
| **Cloud** | Oracle Cloud Infrastructure (OCI) |

---

## 📄 Formatos de documento soportados

| Formato | Extensión | Ejemplo de uso |
|---|---|---|
| PDF | `.pdf` | Manual de onboarding |
| Word | `.docx` | Política de vacaciones |
| Excel | `.xlsx` | Tabla de precios |
| PowerPoint | `.pptx` | Pitch deck de producto |
| Markdown | `.md` | Documentación de API |
| CSV | `.csv` | Base de clientes |
| JSON | `.json` | Configuración de sistema |
| HTML | `.html` | Newsletter interno |

---

## 🗂️ Áreas organizacionales cubiertas

- 👥 **Recursos Humanos** — Políticas, beneficios, onboarding
- 💰 **Financiero** — Gastos, reembolsos, reportes
- ⚙️ **Operacional** — Devoluciones, envíos, procedimientos
- ⚖️ **Legal** — Términos, privacidad, compliance
- 📣 **Marketing** — Catálogo, precios, campañas
- 💻 **Sistemas** — APIs, integraciones, bases de datos

---

## 🚀 Instalación local

### Requisitos previos
- Python 3.11+
- Clave de API de Anthropic

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/agente-corporativo-marketnova.git
cd agente-corporativo-marketnova

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu ANTHROPIC_API_KEY

# 5. Indexar documentos
python src/ingestion/ingest.py

# 6. Iniciar el agente
uvicorn src.api.main:app --reload
```

### Acceder al agente
Abre tu navegador en `http://localhost:8000`

---

## ☁️ Deploy en Oracle Cloud (OCI)

> _Instrucciones de deploy en OCI Compute (Always Free tier) — se completará en la Fase 5_

---

## 👨‍💻 Autor

Desarrollado como parte del desafío **Alura Agentes**.

---

## 📝 Licencia

MIT
