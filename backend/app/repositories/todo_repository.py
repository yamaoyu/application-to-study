from db import db_model
from sqlalchemy.orm import Session
from typing import Optional


class TodoRepository():
    def __init__(self, db: Session):
        self.db = db

    def flush(self):
        self.db.flush()

    def insert_todo(self, title: str, due: str, detail: str, username: str):
        data = db_model.Todo(title=title, due=due, detail=detail, username=username)
        self.db.add(data)

    def get_todo(self, todo_id: int, username: str) -> Optional[db_model.Todo]:
        return self.db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id,
            db_model.Todo.username == username).one_or_none()

    def get_todos(self, username: str, status: bool = None, start_due: str = None, end_due: str = None, title: str = None, ids: Optional[list[int]] = None) -> list[db_model.Todo]:
        sqlstatement = self.db.query(db_model.Todo).filter(
            db_model.Todo.username == username)
        if status is not None:
            sqlstatement = sqlstatement.filter(db_model.Todo.status == status)
        if start_due:
            sqlstatement = sqlstatement.filter(db_model.Todo.due >= start_due)
        if end_due:
            sqlstatement = sqlstatement.filter(db_model.Todo.due <= end_due)
        if title:
            sqlstatement = sqlstatement.filter(db_model.Todo.title.like(f"%{title}%"))
        if ids:
            sqlstatement = sqlstatement.filter(db_model.Todo.todo_id.in_(ids))
        return sqlstatement.all()

    def delete_todo(self, todo_id: int, username: str) -> None:
        self.db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id,
            db_model.Todo.username == username).delete()

    def delete_todos(self, ids: list[int], username: str) -> None:
        self.db.query(db_model.Todo).filter(
            db_model.Todo.todo_id.in_(ids),
            db_model.Todo.username == username).delete()

    def update_todo_content(self, todo: db_model.Todo, title: str = None, due: str = None, detail: str = None) -> None:
        todo.title = title
        todo.due = due
        todo.detail = detail

    def update_todo_status(self, todo: db_model.Todo, status: bool) -> None:
        todo.status = status

    def finish_todos(self, ids: list[int], username: str) -> None:
        self.db.query(db_model.Todo).filter(
            db_model.Todo.todo_id.in_(ids),
            db_model.Todo.username == username).update({db_model.Todo.status: True})
