import traceback
from fastapi import APIRouter, HTTPException, Depends
from db import db_model
from db.database import get_db
from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.models.todo_model import Todo
from sqlalchemy.exc import NoResultFound, IntegrityError
from lib.security import get_current_user
from typing import Optional


router = APIRouter()


@router.post("/todos", status_code=201)
def create_todo(todo: Todo,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    action = todo.action
    due = todo.due
    username = current_user['username']
    try:
        data = db_model.Todo(action=action, username=username, due=due)
        db.add(data)
        db.commit()
        logger.info(f"{username}がTodo作成 内容:{action}")
        return {"message": "以下の内容で作成しました", "action": action, "due": due}
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        if "Duplicate entry" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400, detail="既に登録されている内容です")
        else:
            raise HTTPException(
                status_code=400, detail="Integrity errorが発生しました")
    except Exception:
        logger.error(f"todoの作成に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.get("/todos", status_code=200)
def get_all_todo(status: Optional[bool] = None,
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    try:
        sqlstatement = db.query(db_model.Todo).filter(
            db_model.Todo.username == current_user['username'])
        if status is not None:
            sqlstatement = sqlstatement.filter(db_model.Todo.status == status)
        todos = sqlstatement.all()
        if not todos:
            raise HTTPException(status_code=404,
                                detail="登録された情報はありません")
        logger.info(f"ユーザー名:{current_user['username']}  Todoを全て取得")
        return todos
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"全てのtodoの取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.get("/todos/{todo_id}", status_code=200)
def get_specific_todo(todo_id: int,
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id,
            db_model.Todo.username == current_user['username']).one_or_none()
        if not todo:
            raise HTTPException(status_code=404,
                                detail=f"{todo_id}の情報は未登録です")
        logger.info(f"Todoを取得:{current_user['username']}:ID{todo.todo_id}")
        return todo
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"指定のtodoの取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    try:
        result = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id,
            db_model.Todo.username == current_user['username']).delete()
        if not result:
            raise HTTPException(status_code=404, detail="選択されたタスクは存在しません")
        db.commit()
        logger.info(f"{current_user['username']}がTodoを削除 ID:{todo_id}")
        return {"message": "選択したタスクを削除しました"}
    except HTTPException as http_exception:
        raise http_exception
    except Exception:
        logger.error(f"todoの削除に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.put("/todos/{todo_id}", status_code=200)
def edit_todo(todo_id: int,
              new_action: Todo,
              db: Session = Depends(get_db),
              current_user: dict = Depends(get_current_user)):
    action = new_action.action
    due = new_action.due
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id,
            db_model.Todo.username == current_user['username']).one()
        if todo.status:
            raise HTTPException(status_code=400, detail="終了したアクションは更新できません")
        todo.action = action
        todo.due = due
        db.commit()
        logger.info(f"{current_user['username']}がTodoを編集 ID:{todo.todo_id}")
        return {"message": "Todoを更新しました", "action": action, "due": due}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"id:{todo_id}のデータは登録されていません")
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        if "Duplicate entry" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400, detail="既に登録されている内容です")
        else:
            raise HTTPException(
                status_code=400, detail="Integrity errorが発生しました")
    except HTTPException as http_exception:
        db.rollback()
        raise http_exception
    except Exception:
        logger.error(f"todoの編集に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.put("/todos/finish/{todo_id}", status_code=200)
def finish_todo(todo_id: int,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id,
            db_model.Todo.username == current_user['username']).one()
        if todo.status:
            raise HTTPException(status_code=400, detail="既に終了したタスクです")
        todo.status = True
        logger.info(f"{current_user['username']}がTodoを完了 ID:{todo.todo_id}")
        db.commit()
        return {"message": "以下のタスクのステータスを終了にしました",
                "action": todo.action,
                "status": todo.status}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{todo_id}の内容は登録されていません")
    except HTTPException as http_exception:
        raise http_exception
    except Exception:
        logger.error(f"todoの終了に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
