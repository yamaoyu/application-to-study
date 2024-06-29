from fastapi import APIRouter, HTTPException, Depends
from db import db_model
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.todo_model import Todo
from sqlalchemy.exc import NoResultFound, IntegrityError

router = APIRouter()


@router.post("/todo")
def create_todo(todo: Todo, db: Session = Depends(get_db)):
    action = todo.action
    try:
        data = db_model.Todo(action=action, status=False)
        db.add(data)
        db.commit()
        db.refresh(data)
        return {"action": action}
    except IntegrityError as sqlalchemy_error:
        if "Duplicate entry" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400, detail="既に登録されている内容です")
        else:
            raise HTTPException(
                status_code=400, detail="Integrity errorが発生しました")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"dbの更新に失敗しました{e}")


@router.get("/todo")
def get_all_todo(db: Session = Depends(get_db)):
    todo = db.query(db_model.Todo).filter().all()
    if not todo:
        raise HTTPException(status_code=400,
                            detail="登録された情報はありません。")
    return todo


@router.get("/todo/{todo_id}")
def get_specific_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(db_model.Todo).filter(
        db_model.Todo.todo_id == todo_id).one_or_none()
    if not todo:
        raise HTTPException(status_code=400,
                            detail=f"{todo_id}の情報は未登録です。")
    return todo


@router.delete("/todo/{todo_id}")
def delete_action(todo_id: int, db: Session = Depends(get_db)):
    try:
        db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id).delete()
        db.commit()
        return {"message": "選択したタスクを削除しました。"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail="選択されたタスクは存在しません。")
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=f"削除に失敗しました。\\{e}")


@router.put("/todo/{todo_id}")
def edit_action(todo_id: int,
                new_action: Todo,
                db: Session = Depends(get_db)):
    action = new_action.action
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id).one()
        if todo.status:
            raise HTTPException(status_code=400, detail="終了したアクションは更新できません")
        todo.action = action
        db.commit()
        return {"message": f"更新後のタスク:{action}"}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"id:{todo_id}のデータは登録されていません")
    except IntegrityError as sqlalchemy_error:
        if "Duplicate entry" in str(sqlalchemy_error.orig):
            raise HTTPException(status_code=400, detail="既に登録されている内容です")
        else:
            raise HTTPException(
                status_code=400, detail="Integrity errorが発生しました")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"dbの更新でエラーが発生しました{e}")


@router.put("/todo/finish/{todo_id}")
def finish_action(todo_id: int, db: Session = Depends(get_db)):
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id).one()
        if todo.status:
            raise HTTPException(status_code=400, detail="既に終了したタスクです")
        todo.status = True
        db.commit()
        return {"action": todo.action, "status": todo.status}
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{todo_id}の内容は登録されていません")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"データ更新時にエラーが発生しました。{e}")
