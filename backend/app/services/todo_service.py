import traceback
from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.models.todo_model import (Todo,
                                   UpsertTodoParams,
                                   TodoIdsRequest,
                                   TodosCreateResponse,
                                   TodoGetResponse,
                                   TodosFinishResponse,
                                   TodosDeleteResponse,
                                   TodoEditResponse)
from typing import Optional
from app.repositories.todo_repository import TodoRepository
from app.exceptions import NotFound, Conflict
from app.error_codes import NotFoundCode, ConflictCode, BadRequestCode
from app.utils.validation import get_validation_error_code
from pydantic import ValidationError


class TodoService():
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def create_todos(self, todos: list, username: str) -> TodosCreateResponse:
        success_count = 0
        error_count = 0
        results = []
        for todo in todos:
            title = todo.get("title", None)
            due = todo.get("due", None)
            detail = todo.get("detail", None)
            try:
                UpsertTodoParams(title=title, due=due, detail=detail)
            except ValidationError as exc:
                first_error = exc.errors()[0]
                loc = first_error.get("loc", [])
                field = loc[-1] if loc else None

                reason = get_validation_error_code(
                    error_type=first_error["type"],
                    field=field,
                )
                results.append({
                    "title": title,
                    "due": due,
                    "detail": detail,
                    "result": "error",
                    "reason": reason,
                })
                error_count += 1
                continue
            try:
                with self.repo.begin_nested():
                    self.repo.insert_todo(title, due, detail, username)
                    self.repo.flush()
                    results.append({
                        "title": title,
                        "due": due,
                        "detail": detail,
                        "result": "success",
                        "reason": None,
                    })
                success_count += 1
            except Exception:
                error_count += 1
                logger.error(f"todoの作成に失敗しました\n{traceback.format_exc()}")
                results.append({
                    "title": title,
                    "due": due,
                    "detail": detail,
                    "result": "error",
                    "reason": BadRequestCode.UNEXPECTED_ERROR,
                })

        return TodosCreateResponse(
            success_count=success_count,
            error_count=error_count,
            results=results
        )

    def get_todo(self, todo_id: int, username: str) -> Todo:
        todo = self.repo.get_todo(todo_id, username)
        if not todo:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)
        logger.info(f"Todoを取得:{username}:ID{todo.todo_id}")
        return Todo.model_validate(todo)

    def get_todos(self,
                  status: Optional[bool],
                  start_due: Optional[str],
                  end_due: Optional[str],
                  title: Optional[str],
                  username: str) -> TodoGetResponse:
        todos = self.repo.get_todos(username=username, status=status,
                                    start_due=start_due, end_due=end_due, title=title)
        logger.info(f"ユーザー名:{username}  Todoを全て取得")
        if not todos:
            return TodoGetResponse(todos=[])
        # dbから取得したままでは「db.db_model.Todo」なので整形する
        converted_todos = [Todo.model_validate(todo) for todo in todos]
        return TodoGetResponse(todos=converted_todos)

    def delete_todos(self, params: TodoIdsRequest, username: str) -> TodosDeleteResponse:
        requested_ids = params.ids
        # 削除するTodoが存在するか確認
        todos = self.repo.get_todos(username=username, ids=requested_ids)
        can_delete_ids = set(todo.todo_id for todo in todos)
        missing_ids = set(requested_ids) - can_delete_ids
        self.repo.delete_todos(can_delete_ids, username)
        results = []
        for todo in todos:
            if todo.todo_id in can_delete_ids:
                results.append({
                    "todo_id": todo.todo_id,
                    "title": todo.title,
                    "result": "success",
                    "reason": None
                })
        for id in missing_ids:
            results.append({
                "todo_id": id,
                "title": None,
                "result": "error",
                "reason": NotFoundCode.TODO_NOT_FOUND
            })
        return TodosDeleteResponse(
            success_count=len(can_delete_ids),
            error_count=len(missing_ids),
            results=results
        )

    def edit_todo(self, todo_id: int, new_todo: UpsertTodoParams, username: str) -> TodoEditResponse:
        new_title = new_todo.title
        new_detail = new_todo.detail
        new_due = new_todo.due
        todo = self.repo.get_todo(todo_id, username)
        if not todo:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)
        if todo.status:
            raise Conflict(code=ConflictCode.TODO_ALREADY_FINISHED)
        self.repo.update_todo_content(todo, new_title, new_due, new_detail)
        logger.info(f"{username}がTodoを編集 ID:{todo.todo_id}")
        return TodoEditResponse(
            success_count=1,
            error_count=0,
            results=[
                {
                    "title": new_title,
                    "detail": new_detail,
                    "due": new_due,
                    "result": "success",
                    "reason": None
                }
            ]
        )

    # TODO 別issueにてサービス層の肥大化を解消する(ここに限らず)
    def finish_todos(self, params: TodoIdsRequest, username: str) -> TodosFinishResponse:
        requested_ids = params.ids
        # 終了するTodoが存在するか確認
        todos = self.repo.get_todos(username=username, ids=requested_ids)
        existing_ids = set(todo.todo_id for todo in todos)
        can_finish_ids = set(todo.todo_id for todo in todos if todo.status is False)
        finished_ids = existing_ids - can_finish_ids
        missing_ids = set(requested_ids) - existing_ids
        self.repo.finish_todos(existing_ids, username)
        results = []
        for todo in todos:
            if todo.todo_id in can_finish_ids:
                results.append({
                    "todo_id": todo.todo_id,
                    "title": todo.title,
                    "result": "success",
                    "reason": None
                })

            elif todo.todo_id in finished_ids:
                results.append({
                    "todo_id": todo.todo_id,
                    "title": todo.title,
                    "result": "error",
                    "reason": ConflictCode.TODO_ALREADY_FINISHED
                })
        for id in missing_ids:
            results.append({
                "todo_id": id,
                "title": None,
                "result": "error",
                "reason": NotFoundCode.TODO_NOT_FOUND
            })
        logger.info(f"{username}が複数のTodoを完了 IDs:{requested_ids}")
        return TodosFinishResponse(
            success_count=len(can_finish_ids),
            error_count=len(finished_ids) + len(missing_ids),
            results=results)
