import traceback
from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.models.todo_model import Todo, Todos, IDList
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.repositories.todo_repository import TodoRepository
from app.exceptions import NotFound, BadRequest, Conflict


class TodoService():
    def __init__(self, db: Session):
        self.repo = TodoRepository(db)

    def create_todo(self, todo: Todo, username: str):
        title = todo.title
        due = todo.due
        detail = todo.detail
        try:
            self.repo.insert_todo(title, due, detail, username)
            self.repo.flush()
            logger.info(f"{username}がTodo作成 内容:{title}")
            return {"message": "以下の内容で作成しました", "title": title, "due": due, "detail": detail}
        except IntegrityError as sqlalchemy_error:
            if "Duplicate entry" in str(sqlalchemy_error.orig):
                raise Conflict(detail="既に登録されている内容です")
            raise BadRequest(detail="データの整合性エラーが発生しました。入力データを確認してください")

    def create_todos(self, todos: Todos, username: str):
        error_count = 0
        response_messages = ""
        todos = todos.todos
        for todo in todos:
            Todo(title=todo["title"], detail=todo["detail"], due=todo["due"])
            try:
                title = todo["title"]
                due = todo["due"]
                detail = todo["detail"]
                self.repo.insert_todo(title, due, detail, username)
                self.repo.flush()
                response_messages += f"【Todo作成成功】{title}\n"
            except IntegrityError as sqlalchemy_error:
                error_count += 1
                if "Duplicate entry" in str(sqlalchemy_error.orig):
                    response_messages += f"【Todo作成失敗】{title} : 既に登録されている内容です\n"
                else:
                    response_messages += f"【Todo作成失敗】{title} : 内容を確認してください\n"
            except Exception:
                error_count += 1
                logger.error(f"todoの作成に失敗しました\n{traceback.format_exc()}")
                response_messages += f"【Todo作成失敗】{title} : サーバーでエラーが発生しました。管理者にお問い合わせください\n"

        if error_count > 0:
            raise BadRequest(detail=response_messages[:-1])
        return {"message": response_messages[:-1]}  # 最後の改行を削除して返す

    def get_todo(self, todo_id: int, username: str):
        todo = self.repo.get_todo(todo_id, username)
        if not todo:
            raise NotFound(detail=f"{todo_id}の情報は未登録です")
        logger.info(f"Todoを取得:{username}:ID{todo.todo_id}")
        return todo

    def get_todos(self,
                  status: Optional[bool],
                  start_due: Optional[str],
                  end_due: Optional[str],
                  title: Optional[str],
                  username: str):
        todos = self.repo.get_todos(username=username, status=status,
                                    start_due=start_due, end_due=end_due, title=title)
        if not todos:
            raise NotFound(detail="登録された情報はありません")
        logger.info(f"ユーザー名:{username}  Todoを全て取得")
        return todos

    def delete_todo(self, todo_id: int, username: str):
        todo = self.repo.get_todo(todo_id, username)
        if not todo:
            raise NotFound(detail="選択されたTodoは存在しません")
        self.repo.delete_todo(todo_id, username)
        logger.info(f"{username}がTodoを削除 ID:{todo_id}")

    def delete_todos(self, params: IDList, username: str):
        ids = params.ids
        # 削除するTodoが存在するか確認
        todos = self.repo.get_todos(username=username, ids=ids)
        if not todos:
            raise NotFound(detail="削除リクエストされたTodoは全て存在しません")
        elif len(todos) < len(ids):
            ids_can_delete = set(ids) & set(todo.todo_id for todo in todos)
            title_can_delete = [todo.title for todo in todos]
            self.repo.delete_todos(list(ids_can_delete), username)
            msg = "登録のないTodoが含まれているため、一部のTodo削除処理をスキップしました\n" \
                + f"削除したTodo:{len(ids_can_delete)}件\n" \
                + "".join([f"タイトル:{title}\n" for title in title_can_delete])
            raise BadRequest(detail=msg)
        else:
            self.repo.delete_todos(ids, username)

    def edit_todo(self, todo_id: int, new_todo: Todo, username: str):
        new_title = new_todo.title
        new_detail = new_todo.detail
        new_due = new_todo.due
        try:
            todo = self.repo.get_todo(todo_id, username)
            if not todo:
                raise NotFound(detail=f"id:{todo_id}のデータは登録されていません")
            if todo.status:
                raise Conflict(detail="終了したアクションは更新できません")
            self.repo.update_todo_content(todo, new_title, new_due, new_detail)
            logger.info(f"{username}がTodoを編集 ID:{todo.todo_id}")
            return {"message": "Todoを更新しました", "title": new_title, "due": new_due, "detail": new_detail}
        except IntegrityError as sqlalchemy_error:
            if "Duplicate entry" in str(sqlalchemy_error.orig):
                raise Conflict(detail="既に登録されている内容です")
            raise BadRequest(detail="データの整合性エラーが発生しました。入力データを確認してください")

    def finish_todo(self, todo_id: int, username: str):
        todo = self.repo.get_todo(todo_id, username)
        if not todo:
            raise NotFound(detail="選択されたTodoは存在しません")
        if todo.status:
            raise Conflict(detail="既に終了したTodoです")
        self.repo.update_todo_status(todo, True)
        logger.info(f"{username}がTodoを完了 ID:{todo.todo_id}")
        return {"message": "選択したTodoを終了しました",
                "title": todo.title,
                "status": todo.status}

    def finish_todos(self, params: IDList, username: str):
        ids = params.ids
        msg = ""
        # 終了するTodoが存在するか確認
        todos = self.repo.get_todos(username=username, status=False, ids=ids)
        if not todos:
            raise Conflict(detail="終了リクエストされたTodoは全て存在しないか、既に終了しています")
        can_finish_ids = [todo.todo_id for todo in todos if not todo.status]
        finish_titles = [todo.title for todo in todos if not todo.status]
        if len(can_finish_ids) < len(ids):
            msg = "登録のない/削除済みTodoが含まれているため、一部のTodo終了処理をスキップしました\n"
        self.repo.finish_todos(can_finish_ids, username)
        logger.info(f"{username}が複数のTodoを完了 IDs:{ids}")
        return {"message": f"{msg}{len(can_finish_ids)}件のTodoを終了しました",
                "titles": "\n".join(finish_titles)}
