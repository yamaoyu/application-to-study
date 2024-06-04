from fastapi import APIRouter, HTTPException, Depends
from app.models.time_model import (
    Sample, ResponseTargetTime, TargetTimeIn,
    StudyTimeIn, ResponseStudyTime
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
    target_time = activity.target
    activity.study = study_time
    db.commit()
    message = f"勉強時間を{study_time}時間に設定しました。"
    return {"date": date,
            "study_time": study_time,
            "target_time": target_time,
            "message": message}


@router.get("/finish_today", status_code=200)
async def finish_today_work():
    if today_situation["target"] == "未登録":
        raise HTTPException(status_code=400, detail="本日の目標を入力して下さい")
    elif today_situation["study"] == "未登録":
        raise HTTPException(status_code=400, detail="本日の勉強時間を入力して下さい")
    target = today_situation["target"].hour
    achievement = today_situation["study"].hour
    current_salary["check"] = "完了"
    if achievement >= target:
        current_salary["bonus"] += 1000
        return {
            "message": "目標達成！ボーナス追加", "today bonus": current_salary["bonus"]}
    else:
        diff = target - achievement
        return {"message": f"{diff}時間足りませんでした。"}


@router.post("/sample", status_code=201, response_model=Sample)
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


@router.get("/sample")
async def get_sample(db: Session = Depends(get_db)):
    return db.query(db_model.Activity).all()
