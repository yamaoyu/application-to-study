from fastapi import APIRouter
from app.models.time_model import TimeIn
from datetime import datetime
import pytz

router = APIRouter()

now = format(datetime.now(pytz.timezone('Asia/Tokyo')), "%Y-%m-%d")
today_situation = {"target": 0, "study": 0, "date": now}


@router.get("/today", status_code=200)
async def show_today_situation():
    if today_situation["target"] == 0:
        return {"date": today_situation["date"], "目標勉強時間": "未登録"}
    elif today_situation["study"] == 0:
        return {"date": today_situation["date"],
                "target": today_situation["target"],
                "study time": "未登録"}
    else:
        return {"today situation": today_situation}


@router.post("/today_target", status_code=201, response_model=TimeIn)
async def register_today_target(hour: TimeIn):
    today_situation["target"] = hour
    return hour


@ router.post("/study_time", status_code=201, response_model=TimeIn)
async def register_study_time(hour: TimeIn):
    today_situation["study"] = hour
    return hour
