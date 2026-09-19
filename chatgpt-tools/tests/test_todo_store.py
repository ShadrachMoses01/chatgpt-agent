import json
import pytest
from pathlib import Path
from tools.todo_store import add_todo, list_todos, mark_done, DB_PATH


@pytest.fixture(autouse=True)
def clean_db(monkeypatch):
    tmp = Path("/tmp/test_todos.json")
    if tmp.exists():
        tmp.unlink()
    monkeypatch.setattr("tools.todo_store.DB_PATH", tmp)
    yield
    if tmp.exists():
        tmp.unlink()


class TestTodoStore:
    def test_add_and_list(self):
        todo = add_todo("test task", "high")
        assert todo["title"] == "test task"
        assert todo["priority"] == "high"
        assert todo["done"] is False
        assert "id" in todo

        todos = list_todos()
        assert len(todos) == 1
        assert todos[0]["id"] == todo["id"]

    def test_add_default_priority(self):
        todo = add_todo("default priority")
        assert todo["priority"] == "medium"

    def test_mark_done(self):
        todo = add_todo("finish this")
        marked = mark_done(todo["id"])
        assert marked["done"] is True

        todos = list_todos()
        assert todos[0]["done"] is True

    def test_mark_done_not_found(self):
        result = mark_done("nonexistent")
        assert result == {"error": "todo not found"}

    def test_multiple_todos(self):
        t1 = add_todo("first")
        t2 = add_todo("second")
        todos = list_todos()
        assert len(todos) == 2

    def test_persistence(self):
        add_todo("persist test")
        add_todo("another")
        todos = list_todos()
        assert len(todos) == 2

    def test_dedup_same_title(self):
        t1 = add_todo("duplicate title")
        t2 = add_todo("duplicate title")
        assert "duplicate" in t2
        assert t2["duplicate"] is True
        todos = list_todos()
        assert len(todos) == 1

    def test_allow_same_title_after_done(self):
        t1 = add_todo("recurring task")
        mark_done(t1["id"])
        t2 = add_todo("recurring task")
        assert "duplicate" not in t2
        todos = list_todos()
        assert len(todos) == 2

    def test_default_category(self):
        todo = add_todo("categorized task")
        assert todo.get("category") == "project"

    def test_custom_category(self):
        todo = add_todo("runtime issue", category="runtime")
        assert todo.get("category") == "runtime"
