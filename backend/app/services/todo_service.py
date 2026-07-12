import traceback
from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.models.todo_model import (Todo,
                                   TodoIdsRequest,
                                   TodosCreateResponse,
                                   TodoGetResponse,
                                   TodosFinishResponse,
                                   TodosDeleteResponse,
                                   TodoEditResponse)
from typing import Optional
from app.repositories.todo_repository import TodoRepository
from app.exceptions import NotFound, BadRequest, Conflict
from app.error_codes import NotFoundCode, ConflictCode, BadRequestCode


class TodoService():
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def create_todos(self, todos: list[Todo], username: str) -> TodosCreateResponse:
        success_count = 0
        error_count = 0
        results = []
        for todo in todos:
            title = todo.title
            due = todo.due
            detail = todo.detail
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

        if error_count == len(todos):
            raise BadRequest(code=BadRequestCode.UNEXPECTED_ERROR)
        return TodosCreateResponse(
            success_count=success_count,
            error_count=error_count,
            results=results
        )

    def get_todo(self, todo_id: int, username: str) -> TodoGetResponse:
        todo = self.repo.get_todo(todo_id, username)
        if not todo:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)
        logger.info(f"Todoを取得:{username}:ID{todo.todo_id}")
        return TodoGetResponse.model_validate(todo)

    def get_todos(self,
                  status: Optional[bool],
                  start_due: Optional[str],
                  end_due: Optional[str],
                  title: Optional[str],
                  username: str) -> list[TodoGetResponse]:
        todos = self.repo.get_todos(username=username, status=status,
                                    start_due=start_due, end_due=end_due, title=title)
        if not todos:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)
        logger.info(f"ユーザー名:{username}  Todoを全て取得")
        return [TodoGetResponse.model_validate(todo) for todo in todos]

    def delete_todos(self, params: TodoIdsRequest, username: str) -> TodosDeleteResponse:
        ids = params.ids
        # 削除するTodoが存在するか確認
        todos = self.repo.get_todos(username=username, ids=ids)
        if not todos:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)
        ids_can_delete = [todo.todo_id for todo in todos]
        self.repo.delete_todos(ids_can_delete, username)
        results = []
        # 削除できるのは存在するTodoのみなので、削除できたTodoの情報を返す
        # 存在しないTodoの情報は返せないので、削除できなかったTodoの情報は返さない
        for todo in todos:
            results.append({
                "title": todo.title,
                "due": todo.due,
                "detail": todo.detail,
                "result": "success",
                "reason": None
            })
        return TodosDeleteResponse(
            success_count=len(ids_can_delete),
            error_count=len(ids) - len(ids_can_delete),
            results=results
        )

    def edit_todo(self, todo_id: int, new_todo: Todo, username: str) -> TodoEditResponse:
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

    def finish_todos(self, params: TodoIdsRequest, username: str) -> TodosFinishResponse:
        ids = params.ids
        # 終了するTodoが存在するか確認
        todos = self.repo.get_todos(username=username, ids=ids)
        if not todos:
            raise NotFound(code=NotFoundCode.TODO_NOT_FOUND)
        can_finish_ids = set(todo.todo_id for todo in todos if todo.status is False)
        if len(can_finish_ids) == 0:
            raise Conflict(code=ConflictCode.TODO_ALREADY_FINISHED)
        self.repo.finish_todos(list(can_finish_ids), username)
        results = [
            {
                "title": todo.title,
                "detail": todo.detail,
                "due": todo.due,
                "result": "success",
                "reason": None
            }
            for todo in todos if todo.todo_id in can_finish_ids]
        logger.info(f"{username}が複数のTodoを完了 IDs:{ids}")
        return TodosFinishResponse(
            success_count=len(can_finish_ids),
            error_count=len(ids) - len(can_finish_ids),
            results=results)
