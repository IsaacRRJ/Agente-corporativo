import secrets
import json
from pathlib import Path

EMPLOYEES_FILE = Path(__file__).parent / "employees.json"
_sessions: dict[str, dict] = {}


def _load_employees() -> dict[str, dict]:
    data = json.loads(EMPLOYEES_FILE.read_text(encoding="utf-8"))
    return {e["code"].upper(): e for e in data["employees"]}


def login(code: str) -> dict | None:
    employees = _load_employees()
    employee = employees.get(code.upper().strip())
    if employee is None:
        return None
    token = secrets.token_hex(32)
    _sessions[token] = employee
    return {"token": token, "employee": employee}


def get_session(token: str) -> dict | None:
    return _sessions.get(token)


def logout(token: str) -> None:
    _sessions.pop(token, None)
