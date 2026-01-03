from fastapi import APIRouter, Depends, Body
from app.models.time_model import (
    TargetTimeIn, MultiTargetTimeIn,
    ActualTimeIn, MultiActualTimeIn,
    RegisterActivities, ValidateStatus
)
from app.models.common_model import CheckDate, CheckYearMonth, CheckYear
from db.database import get_db
from lib.security import get_current_user
from sqlalchemy.orm import Session
from app.services.time_service import TimeService

router = APIRouter()


def get_time_service(db: Session = Depends(get_db)) -> TimeService:
    return TimeService(db)


@router.get("/activities/{year}/{month}/{day}", status_code=200)
def get_day_activity(params: CheckDate = Depends(),
                     db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    """ 特定日の活動実績を確認する """
    service = get_time_service(db)
    return service.get_day_activity(params.year, params.month, params.day, current_user["username"])


@router.post("/activities/{year}/{month}/{day}/target",
             status_code=201,
             response_model=RegisterActivities)
def register_target_time(target: TargetTimeIn,
                         date: CheckDate = Depends(),
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """ 目標活動時間を登録する """
    target_time = target.target_time
    service = get_time_service(db)
    return service.register_target_time(target_time, date.year, date.month, date.day, current_user["username"])


@router.post("/activities/multi/target", status_code=201)
def register_multi_target_time(activities: MultiTargetTimeIn,
                               db: Session = Depends(get_db),
                               current_user: dict = Depends(get_current_user)):
    service = get_time_service(db)
    data = [{"date": activity["date"], "target_time": activity["target_time"]}
            for activity in activities.activities]
    return service.register_target_time_bulk(data, current_user["username"])


@router.put("/activities/multi/actual", status_code=200)
def update_multi_actual_time(activities: MultiActualTimeIn,
                             db: Session = Depends(get_db),
                             current_user: dict = Depends(get_current_user)):
    """ 複数日の活動時間を登録する """
    service = get_time_service(db)
    data = [{"date": activity["date"], "actual_time": activity["actual_time"]}
            for activity in activities.activities]
    return service.register_actual_time_bulk(data, current_user["username"])


@router.put("/activities/{year}/{month}/{day}/actual",
            status_code=200,
            response_model=RegisterActivities)
def update_actual_time(actual: ActualTimeIn,
                       date: CheckDate = Depends(),
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    """ 目標時間が登録済みの場合、活動時間を入力 """
    print(actual, actual.actual_time)
    service = get_time_service(db)
    return service.register_actual_time(actual.actual_time, date.year, date.month, date.day, current_user["username"])


@router.put("/activities/{year}/{month}/{day}/finish",
            status_code=200,
            response_model=RegisterActivities)
def finish_activity(params: CheckDate = Depends(),
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    """ 特定日の作業時間を確定し、目標を達成しているのかを確認する """
    service = get_time_service(db)
    return service.finish_activity(params.year, params.month, params.day, current_user["username"])


@router.put("/activities/multi/finish", status_code=200)
def finish_multi_activities(request: dict = Body(),
                            db: Session = Depends(get_db),
                            current_user: dict = Depends(get_current_user)):
    """ 複数日の活動を確定する """
    service = get_time_service(db)
    return service.finish_activities(request.get("dates", []), current_user["username"])


@router.get("/activities/{year}/{month}", status_code=200)
def get_month_activities(params: CheckYearMonth = Depends(),
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """ 特定月のデータを取得 """
    service = get_time_service(db)
    return service.get_month_activities(params.year, params.month, current_user["username"])


@router.get("/activities/{year:int}", status_code=200)
def get_year_activities(param: CheckYear = Depends(),
                        db: Session = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    """ 特定年のデータを取得 """
    service = get_time_service(db)
    return service.get_year_activities(param.year, current_user["username"])


@router.get("/activities/total", status_code=200)
def get_all_activities(db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    """ 全期間を集計したデータを取得 """
    service = get_time_service(db)
    return service.get_all_activities(current_user["username"])


@router.get("/activities", status_code=200)
def get_activities_by_status(param: ValidateStatus = Depends(),
                             db: Session = Depends(get_db),
                             current_user: dict = Depends(get_current_user)):
    """ 日ごとの活動実績をステータスごとに取得 """
    service = get_time_service(db)
    return service.get_activities_by_status(param.status, current_user["username"])
