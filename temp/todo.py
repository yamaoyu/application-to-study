from fastapi import APIRouter, HTTPException, Depends
from db import db_model
from db.database import get_db
from sqlalchemy.orm import Session
from app.models.todo_model import TodoIn, UpdateAction
import re

router = APIRouter()


@router.post("/todo")
def create_todo(todo: TodoIn, db: Session = Depends(get_db)):
    action = todo.action
    date = todo.date
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    try:
        data = db_model.Todo(action=action, date=date, status=False)
        db.add(data)
        db.commit()
        db.refresh(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"dbの更新に失敗しました{e}")
    return {"action": action, "date": date}


@router.get("/todo/{date}")
def get_specific_todo(date: str, db: Session = Depends(get_db)):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    todo = db.query(db_model.Todo).filter(db_model.Todo.date == date).all()
    if not todo:
        raise HTTPException(status_code=400,
                            detail=f"{date}の情報は未登録です。")
    return todo


@router.delete("/todo/{todo_id}")
def delete_action(todo_id: int, db: Session = Depends(get_db)):
    try:
        db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id).delete()
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=f"削除に失敗しました。\\{e}")
    return {"message": "選択したタスクを削除しました。"}


@router.put("/todo/{todo_id}")
def edit_action(todo_id: int,
                new_action: UpdateAction,
                db: Session = Depends(get_db)):
    action = new_action.action
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id).one()
    except Exception:
        raise HTTPException(status_code=400, detail=f"{todo_id}の内容は登録されていません")
    todo.action = action
    db.commit()
    return {"message": f"更新後のタスク:{action}"}


@router.put("/todo/finish/{todo_id}")
def finish_action(todo_id: int, db: Session = Depends(get_db)):
    try:
        todo = db.query(db_model.Todo).filter(
            db_model.Todo.todo_id == todo_id).one()
    except Exception:
        raise HTTPException(status_code=400,
                            detail=f"{todo_id}の内容は登録されていません")
    todo.status = True
    db.commit()
    return todo
