import json
import uuid
from pathlib import Path


# Anchored to the package directory (not the process working directory) so
# todos land in the same file regardless of where the bridge server or a
# tool runner is started from.
DB_PATH = Path(__file__).resolve().parent.parent / "todos.json"


def _load():
    if not DB_PATH.exists():
        return []
    return json.loads(DB_PATH.read_text())


def _save(data):
    tmp = DB_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(DB_PATH)


def add_todo(title: str, priority: str = "medium", category: str = "project"):
    todos = _load()

    existing = [t for t in todos if t["title"] == title and not t["done"]]
    if existing:
        return {"duplicate": True, "todo": existing[0]}

    todo = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "priority": priority,
        "category": category,
        "done": False,
    }

    todos.append(todo)
    _save(todos)
    return todo


def list_todos():
    return _load()


def mark_done(todo_id: str):
    todos = _load()

    for t in todos:
        if t["id"] == todo_id:
            t["done"] = True
            _save(todos)
            return t

    return {"error": "todo not found"}
