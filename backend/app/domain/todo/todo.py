from dataclasses import dataclass
from datetime import date

from app.domain.todo.exceptions import (
    InvalidTodo,
    TodoAlreadyFinished,
    TodoValidationReason,
)


@dataclass
class Todo:
    todo_id: int
    title: str
    detail: str | None
    due: date
    status: bool

    def finish(self) -> None:
        if self.status:
            raise TodoAlreadyFinished()
        self.status = True

    def edit(self, title: str, detail: str | None, due: date) -> None:
        if self.status:
            raise TodoAlreadyFinished()

        self.title = title
        self.detail = detail
        self.due = due


@dataclass(frozen=True)
class TodoDraft:
    title: str
    due: date
    detail: str | None

    @classmethod
    def create(cls, title: str, due: str, detail: str | None) -> "TodoDraft":
        return cls(
            title=cls._validate_title(title),
            due=cls._validate_due(due),
            detail=cls._validate_detail(detail),
        )

    @staticmethod
    def _validate_title(title: str) -> str:
        if not title:
            raise InvalidTodo(
                TodoValidationReason.TITLE_REQUIRED,
                field="title",
                detail="Title is required.",
            )
        if len(title) > 32:
            raise InvalidTodo(
                TodoValidationReason.TITLE_TOO_LONG,
                field="title",
                detail="Title is too long.",
            )
        return title

    @staticmethod
    def _validate_due(due: str) -> date:
        if not due:
            raise InvalidTodo(
                TodoValidationReason.DUE_REQUIRED,
                field="due",
                detail="Due date is required.",
            )
        try:
            year, month, day = map(int, due.split("-"))
            return date(year, month, day)
        except ValueError as e:
            raise InvalidTodo(
                TodoValidationReason.INVALID_DUE,
                field="due",
                detail="Invalid due date.",
            ) from e

    @staticmethod
    def _validate_detail(detail: str | None) -> str | None:
        if not isinstance(detail, str):
            return detail
        if len(detail) > 200:
            raise InvalidTodo(
                TodoValidationReason.DETAIL_TOO_LONG,
                field="detail",
                detail="Detail is too long.",
            )
        return detail
