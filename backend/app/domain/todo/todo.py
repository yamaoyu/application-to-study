from dataclasses import dataclass
from app.domain.todo.exceptions import TodoAlreadyFinished, InvalidTodo, TodoValidationReason
from typing import Optional
from datetime import date


@dataclass
class Todo:
    todo_id: int
    title: str
    detail: Optional[str]
    due: date
    status: bool

    def finish(self) -> None:
        if self.status:
            raise TodoAlreadyFinished()
        self.status = True

    def edit(self, title: str, detail: Optional[str], due: date) -> None:
        if self.status:
            raise TodoAlreadyFinished()

        self.title = title
        self.detail = detail
        self.due = due


@dataclass(frozen=True)
class TodoDraft:
    title: str
    due: date
    detail: Optional[str]

    @classmethod
    def create(cls, title: str, due: str, detail: Optional[str]) -> "TodoDraft":
        return cls(
            title=cls._validate_title(title),
            due=cls._validate_due(due),
            detail=cls._validate_detail(detail)
        )

    @staticmethod
    def _validate_title(title: str) -> str:
        if not title:
            raise InvalidTodo(TodoValidationReason.TITLE_REQUIRED)
        if len(title) > 32:
            raise InvalidTodo(TodoValidationReason.TITLE_TOO_LONG)
        return title

    @staticmethod
    def _validate_due(due: str) -> date:
        if not due:
            raise InvalidTodo(TodoValidationReason.DUE_REQUIRED)
        try:
            year, month, day = map(int, due.split("-"))
            return date(year, month, day)
        except Exception:
            raise InvalidTodo(TodoValidationReason.INVALID_DUE)

    @staticmethod
    def _validate_detail(detail: Optional[str]) -> str | None:
        if isinstance(detail, str) and len(detail) > 200:
            raise InvalidTodo(TodoValidationReason.DETAIL_TOO_LONG)
        return detail
