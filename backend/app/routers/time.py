from fastapi import APIRouter, HTTPException, Depends
from app.models.time_model import (
    Sample, ResponseTargetTime, TargetTimeIn,
    StudyTimeIn, ResponseStudyTime, DateIn
)
from datetime import datetime
import pytz
from db import db_model
from db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

now = format(datetime.now(pytz.timezone('Asia/Tokyo')), "%Y-%m-%d")
today_situation = {"target": "未登録", "study": "未登録", "date": now}
current_salary = {"base": "未登録", "bonus": 0, "check": "未完了"}


@router.get("/today", status_code=200)
async def show_today_situation():
    if today_situation["target"] == "未登録":
        return {"today situation": today_situation,
                "present achivement": current_salary}
    elif today_situation["study"] == 0:
        return {"today situation": today_situation,
                "present achivement": current_salary}
    else:
        if current_salary["base"] == "未登録":
            raise HTTPException(status_code=400, detail="月収を登録して下さい")
        elif current_salary["check"] == "未完了":
            raise HTTPException(status_code=400, detail="本日の成果を確認して下さい")
        added_salary = current_salary["base"].salary + current_salary["bonus"]
        return {
            "today situation": today_situation,
            "present achivement": current_salary,
            "current total": added_salary
        }


@router.post("/target_time",
             status_code=201,
             response_model=ResponseTargetTime)
async def register_today_target(target: TargetTimeIn,
                                db: Session = Depends(get_db)):
    """ 目標勉強時間を登録、登録済みなら更新する """
    target_hour = target.target_hour
    date = target.date
    data = db_model.Activity(date=date, target=target_hour)
    try:
        db.add(data)
        db.commit()
        db.refresh(data)
    except Exception:
        raise HTTPException(status_code=400,
                            detail=f"{data.date}の目標時間は既に登録済みです")
    message = f"本日の目標時間を{target_hour}時間に設定しました"
    return {"target_hour": target_hour, "date": date, "message": message}


@router.post("/study_time",
             status_code=201,
             response_model=ResponseStudyTime)
async def register_study_time(study: StudyTimeIn,
                              db: Session = Depends(get_db)):
    """ 目標時間が登録済みの場合、勉強時間を入力 """
    date = study.date
    study_time = study.study_time
    try:
        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date).one()
    except Exception:
        raise HTTPException(status_code=400, detail="先に本日の目標を入力して下さい")
    activity.study = study_time
    db.commit()
    message = f"勉強時間を{study_time}時間に設定しました。"
    return {"date": date,
            "study_time": study_time,
            "target_time": activity.target,
            "message": message}


@router.get("/finish", status_code=200)
async def finish_today_work(date: DateIn, db: Session = Depends(get_db)):
    date = date.date
    year_month = date[:7]
    try:
        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date).one()
    except Exception:
        raise HTTPException(status_code=400, detail=f"{date}の情報は登録されていません")
    target_hour = activity.target
    study_hour = activity.study
    if study_hour is None:
        raise HTTPException(status_code=400, detail="本日の勉強時間を登録して下さい")
    elif activity.is_achieved is not None:
        raise HTTPException(status_code=400, detail=f"{date}の実績は登録済みです")
    elif study_hour >= target_hour:
        activity.is_achieved = True
        message = "目標達成！ボーナス追加！"
        salary = db.query(db_model.Salary).filter(
            db_model.Salary.year_month == year_month).one()
        salary.bonus += 1000
    else:
        activity.is_achieved = False
        diff = round((target_hour - study_hour), 1)
        message = f"{diff}時間足りませんでした"
    db.commit()
    return {
        "date": date,
        "target hour": target_hour,
        "study hour": study_hour,
        "is achieved": activity.is_achieved,
        "message": message}


@router.get("/month")
async def get_month_situation(date: DateIn, db: Session = Depends(get_db)):
    year_month = date.date
    activity = db.query(db_model.Activity).filter(
        db_model.Activity.date.like(f"{year_month}%")).all()
    if not activity:
        raise HTTPException(status_code=400,
                            detail=f"{year_month}内の活動は登録されていません")
    salary = db.query(db_model.Salary).filter(
        db_model.Salary.year_month == year_month).one()
    if not salary:
        raise HTTPException(status_code=400,
                            detail=f"{year_month}の給料は登録されていません")
    total_monthly_income = salary.monthly_income + salary.bonus
    success_days = [act for act in activity if act.is_achieved is True]
    return {"total_monthly_income": total_monthly_income,
            "base income": salary.monthly_income,
            "study bonus": salary.bonus,
            "success days": len(success_days),
            "activity lists": activity}


@ router.post("/sample", status_code=201, response_model=Sample)
async def sample(sample: Sample, db: Session = Depends(get_db)):
    try:
        target = sample.target
        study = sample.study
        if study >= target:
            is_achieved = True
        else:
            is_achieved = False
        data = db_model.Activity(date=now, target=target,
                                 study=study, is_achieved=is_achieved)
        db.add(data)
        db.commit()
        db.refresh(data)
        return data
    except Exception:
        raise HTTPException(status_code=400, detail="データ登録に失敗")


@ router.get("/all")
async def get_all_activities(db: Session = Depends(get_db)):
    return db.query(db_model.Activity).all()
