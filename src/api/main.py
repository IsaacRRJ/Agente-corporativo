import json
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parents[1]))
from agent.agent import answer
from auth.auth import login as auth_login, get_session, logout as auth_logout

FEEDBACK_LOG = Path(__file__).parents[2] / "logs" / "feedback.jsonl"

app = FastAPI(title="Agente Corporativo MarketNova")
security = HTTPBearer(auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = Path(__file__).parents[2] / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


# --- Auth dependency ---

def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Se requiere autenticación")
    session = get_session(credentials.credentials)
    if session is None:
        raise HTTPException(status_code=401, detail="Token inválido o sesión expirada")
    return session


# --- Models ---

class LoginRequest(BaseModel):
    code: str

class AskRequest(BaseModel):
    query: str
    category: str | None = None

class FeedbackRequest(BaseModel):
    query: str
    response: str
    rating: str


# --- Endpoints ---

@app.get("/")
def root():
    return FileResponse(
        str(frontend_dir / "index.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/login")
def login(req: LoginRequest):
    result = auth_login(req.code)
    if result is None:
        raise HTTPException(status_code=401, detail="Código de empleado inválido")
    return result


@app.get("/me")
def me(session: dict = Depends(require_auth)):
    return session


@app.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        auth_logout(credentials.credentials)
    return {"ok": True}


@app.post("/ask")
def ask(req: AskRequest, session: dict = Depends(require_auth)):
    result = answer(req.query, category=req.category)
    return result


@app.post("/feedback")
def feedback(req: FeedbackRequest, session: dict = Depends(require_auth)):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "employee_code": session.get("code"),
        "employee_name": session.get("name"),
        "query": req.query,
        "response": req.response,
        "rating": req.rating,
    }
    FEEDBACK_LOG.parent.mkdir(exist_ok=True)
    with open(FEEDBACK_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"ok": True}
