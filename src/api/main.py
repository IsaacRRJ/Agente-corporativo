import json
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parents[1]))
from agent.agent import answer

FEEDBACK_LOG = Path(__file__).parents[2] / "logs" / "feedback.jsonl"

app = FastAPI(title="Agente Corporativo MarketNova")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = Path(__file__).parents[2] / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


# --- Modelos ---

class AskRequest(BaseModel):
    query: str
    category: str | None = None

class FeedbackRequest(BaseModel):
    query: str
    response: str
    rating: str  # "positive" | "negative"


# --- Endpoints ---

@app.get("/")
def root():
    return FileResponse(str(frontend_dir / "index.html"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest):
    result = answer(req.query, category=req.category)
    return result


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": req.query,
        "response": req.response,
        "rating": req.rating,
    }
    FEEDBACK_LOG.parent.mkdir(exist_ok=True)
    with open(FEEDBACK_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"ok": True}
