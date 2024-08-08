from logging import getLogger, basicConfig, INFO
from fastapi import APIRouter, HTTPException, Depends
from db import db_model
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.todo_model import Todo
from sqlalchemy.exc import NoResultFound, IntegrityError
from security import get_current_user


router = APIRouter()

basicConfig(level=INFO, format="%(levelname)s: %(message)s")
logger = getLogger(__name__)


@router.post("/todo", status_code=201)
def create_todo(todo: Todo,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    action = todo.action
    username = current_user['username']
    try:
        data = db_model.Todo(action=action, username=username)
        db.add(data)
        db.commit()
        db.refresh(data)
        logger.info(f"{username}がTodo作成 内容:{action}")
        return {"action": action}
    except IntegrityError as sqlalchemy_error:
        db.rollback()
        if "Duplicate entry" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400, detail="既に登録されている内容です")
        else:
            raise HTTPException(
                status_code=400, detail="Integrity errorが発生しました")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Todo作成処理中にエラーが発生しました: {e}")


@router.get("/todo", status_code=200)
def get_all_todo(db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.username == current_user['username']).all()
        if not todo:
            raise HTTPException(status_code=404,
                                detail="登録された情報はありません。")
        logger.info(f"ユーザー名:{current_user['username']}  Todoを全て取得")
        return todo
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"todo取得処理にエラーが発生しました:n {e}")


@router.get("/todo/{todo_id}", status_code=200)
def get_specific_todo(todo_id: int,
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id,
            db_model.Todo.username == current_user['username']).one_or_none()
        if not todo:
            raise HTTPException(status_code=404,
                                detail=f"{todo_id}の情報は未登録です。")
        logger.info(f"Todoを取得:{current_user['username']}:ID{todo.todo_id}")
        return todo
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"todo取得処理にエラーが発生しました: {e}")


@router.delete("/todo/{todo_id}", status_code=204)
def delete_action(todo_id: int,
                  db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    try:
        result = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id,
            db_model.Todo.username == current_user['username']).delete()
        if not result:
            raise HTTPException(status_code=404, detail="選択されたタスクは存在しません。")
        db.commit()
        logger.info(f"{current_user['username']}がTodoを削除 ID:{todo_id}")
        return
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Todoの削除処理に失敗しました: {e}")


@router.put("/todo/{todo_id}", status_code=200)
def edit_action(todo_id: int,
                new_action: Todo,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    action = new_action.action
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id,
            db_model.Todo.username == current_user['username']).one()
        if todo.status:
            raise HTTPException(status_code=400, detail="終了したアクションは更新できません")
        todo.action = action
        db.commit()
        logger.info(f"{current_user['username']}がTodoを編集 ID:{todo.todo_id}")
        return {"message": f"更新後のタスク:{action}"}
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
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Todoの更新処理でエラーが発生しました: {e}")


@router.put("/todo/finish/{todo_id}", status_code=200)
def finish_action(todo_id: int,
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
        return {"action": todo.action, "status": todo.status}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{todo_id}の内容は登録されていません")
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Todo終了処理中にエラーが発生しました:n {e}")
