from fastapi import APIRouter, HTTPException
from app.models.time_model import TimeIn, RegisterSalary
from datetime import datetime
import pytz

router = APIRouter()

now = format(datetime.now(pytz.timezone('Asia/Tokyo')), "%Y-%m-%d")
today_situation = {"target": "未登録", "study": "未登録", "date": now}
current_salary = {"base": "未登録", "bonus": 0}


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
        added_salary = current_salary["base"].salary + current_salary["bonus"]
        return {
            "today situation": today_situation,
            "present achivement": current_salary,
            "current total": added_salary
        }


@router.post("/today_target", status_code=201, response_model=TimeIn)
async def register_today_target(hour: TimeIn):
    today_situation["target"] = hour
    return hour


@router.post("/study_time", status_code=201, response_model=TimeIn)
async def register_study_time(hour: TimeIn):
    if today_situation["target"] == "未登録":
        raise HTTPException(status_code=400, detail="先に本日の目標を入力して下さい")
    today_situation["study"] = hour
    return hour


@router.get("/finish_today", status_code=200)
async def finish_today_work():
    if today_situation["target"] == "未登録":
        raise HTTPException(status_code=400, detail="本日の目標を入力して下さい")
    elif today_situation["study"] == "未登録":
        raise HTTPException(status_code=400, detail="本日の勉強時間を入力して下さい")
    target = today_situation["target"].hour
    achievement = today_situation["study"].hour
    if achievement >= target:
        current_salary["bonus"] += 1000
        return {
            "message": "目標達成！ボーナス追加", "today bonus": current_salary["bonus"]}
    else:
        diff = target - achievement
        return {"message": f"{diff}時間足りませんでした。"}


@router.post("/register_salary")
async def register_salary(salary: RegisterSalary):
    current_salary["base"] = salary
    return salary
