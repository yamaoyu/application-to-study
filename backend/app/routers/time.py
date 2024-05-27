from fastapi import APIRouter
from app.models.time_model import RegisterTime

router = APIRouter()

today_situation = {"target": 0, "study": 0}


@router.get("/today")
async def show_today_situation():
    if today_situation["target"] == 0:
        return {"目標勉強時間": "未登録"}
    elif today_situation["study"] == 0:
        return {"target": today_situation["target"], "study time": "未登録"}
    else:
        return {"today situation": today_situation}


@router.post("/today_target", status_code=201, response_model=RegisterTime)
async def register_today_target(hour: RegisterTime):
    today_situation["target"] = hour
    return today_situation


@router.post("/study_time", status_code=201, response_model=RegisterTime)
async def register_study_time(hour: RegisterTime):
    today_situation["study"] = hour
    return hour
