import re
from fastapi import APIRouter, HTTPException, Depends
from app.models.time_model import (
    ResponseTargetTime, TargetTimeIn,
    ActualTimeIn, ResponseStudyTime, DateIn
)
from db import db_model
from db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

router = APIRouter()


@router.get("/today", status_code=200)
def show_today_situation(date: DateIn, db: Session = Depends(get_db)):
    """ その日の勉強時間を確認する """
    date = date.date
    # dateのフォーマットがYYYY-MM-DDか確認
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    try:
        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date).one()
    except NoResultFound:
        raise HTTPException(status_code=400, detail=f"{date}の情報は登録されていません")
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    target_time = activity.target
    if not target_time:
        return {"date": date, "target time": "未設定", "actual time": "未設定"}

    actual_time = activity.actual
    if not actual_time:
        return {"date": date, "target time": target_time, "actual time": "未設定"}

    is_achieved = activity.is_achieved
    if is_achieved is None:
        return {"date": date, "target time": target_time,
                "actual time": actual_time, "is achieved": "未完了"}

    bonus = lambda is_achieved: 0.1 if is_achieved else 0  # noqa
    return {"date": date, "target time": target_time,
            "actual time": actual_time, "is achieved": is_achieved,
            "bonus": bonus(is_achieved)}


@router.post("/target_time",
             status_code=201,
             response_model=ResponseTargetTime)
def register_today_target(target: TargetTimeIn,
                          db: Session = Depends(get_db)):
    """ 目標勉強時間を登録、登録済みなら更新する """
    target_hour = target.target_hour
    date = target.date
    # dateのフォーマットがYYYY-MM-DDか確認
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    data = db_model.Activity(date=date, target=target_hour)
    try:
        db.add(data)
        db.commit()
        db.refresh(data)
    except Exception:
        raise HTTPException(status_code=400,
                            detail=f"{data.date}の目標時間は既に登録済みです")
    message = f"{date}の目標時間を{target_hour}時間に設定しました"
    return {"target_hour": target_hour, "date": date, "message": message}


@router.put("/actual_time",
            status_code=201,
            response_model=ResponseStudyTime)
def register_actual_time(actual: ActualTimeIn,
                         db: Session = Depends(get_db)):
    """ 目標時間が登録済みの場合、勉強時間を入力 """
    actual_time = actual.actual_time
    date = actual.date
    # dateのフォーマットがYYYY-MM-DDか確認
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    try:
        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date).one()
    except Exception:
        raise HTTPException(status_code=400, detail=f"先に{date}の目標を入力して下さい")
    if activity.is_achieved is None:
        activity.actual = actual_time
        db.commit()
        message = f"勉強時間を{actual_time}時間に設定しました。"
        return {"date": date,
                "actual_time": actual_time,
                "target_time": activity.target,
                "message": message}
    else:
        raise HTTPException(status_code=400,
                            detail=f"{date}の活動実績は既に確定済みです。変更できません")


@router.put("/finish", status_code=200)
def finish_today_work(date: DateIn, db: Session = Depends(get_db)):
    """ その日の作業時間を確定し、目標を達成しているのかを確認する """
    date = date.date
    # dateのフォーマットがYYYY-MM-DDか確認
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    year_month = date[:7]
    try:
        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date).one()
    except NoResultFound:
        raise HTTPException(status_code=400, detail=f"{date}の情報は登録されていません")

    target_hour = activity.target
    actual_hour = activity.actual

    if actual_hour is None:
        raise HTTPException(status_code=400, detail="本日の勉強時間を登録して下さい")
    elif activity.is_achieved is not None:
        raise HTTPException(status_code=400, detail=f"{date}の実績は登録済みです")
    # 達成している場合はIncomeテーブルのボーナスを加算する。
    if actual_hour >= target_hour:
        try:
            salary = db.query(db_model.Income).filter(
                db_model.Income.year_month == year_month).one()
            activity.is_achieved = True
            message = "目標達成！ボーナス追加！"
            salary.bonus = float(salary.bonus) + 0.1
        except NoResultFound:
            raise HTTPException(status_code=400,
                                detail=f"{year_month}の収入が未登録です。")
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
    # 達成していない場合はIncomeテーブルを更新しない
    else:
        activity.is_achieved = False
        diff = round((target_hour - actual_hour), 1)
        message = f"{diff}時間足りませんでした"
    db.commit()
    return {
        "date": date,
        "target hour": target_hour,
        "actual hour": actual_hour,
        "is achieved": activity.is_achieved,
        "message": message}


@router.get("/month")
def get_month_situation(date: DateIn, db: Session = Depends(get_db)):
    """ 月毎のデータを取得 """
    year_month = date.date
    # dateのフォーマットがYYYY-MMか確認
    if not re.match(r"^\d{4}-\d{2}$", year_month):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM")
    activity = db.query(db_model.Activity).filter(
        db_model.Activity.date.like(f"{year_month}%")).all()
    if not activity:
        raise HTTPException(status_code=400,
                            detail=f"{year_month}内の活動は登録されていません")
    try:
        salary = db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month).one()
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f"{year_month}の給料は登録されていません")
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    total_monthly_income = salary.monthly_income + salary.bonus
    success_days = [act for act in activity if act.is_achieved is True]
    return {"total_monthly_income": total_monthly_income,
            "base income": salary.monthly_income,
            "total bonus": salary.bonus,
            "success days": len(success_days),
            "activity lists": activity}
