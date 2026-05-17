from fastapi import APIRouter, Depends
from app.models.time_model import MultiTargetTimeIn, MultiActualTimeIn, ValidateStatus, MultiFinishActivityIn
from app.models.common_model import CheckDate, CheckYearMonth, CheckYear
from db.database import get_db
from app.dependencies.auth import get_current_user
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
    # パスパラメータで受け取る年、月、日は文字列のため、intに変換する
    year = int(params.year)
    month = int(params.month)
    day = int(params.day)
    return service.get_day_activity(year, month, day, current_user["username"])


@router.post("/activities/multi/target", status_code=201)
def register_multi_target_time(activities: MultiTargetTimeIn,
                               db: Session = Depends(get_db),
                               current_user: dict = Depends(get_current_user)):
    service = get_time_service(db)
    data = [{"date": activity.date, "target_time": activity.target_time}
            for activity in activities.activities]
    return service.register_target_time_bulk(data, current_user["username"])


@router.put("/activities/multi/actual", status_code=200)
def update_multi_actual_time(activities: MultiActualTimeIn,
                             db: Session = Depends(get_db),
                             current_user: dict = Depends(get_current_user)):
    """ 複数日の活動時間を登録する """
    service = get_time_service(db)
    data = [{"date": activity.date, "actual_time": activity.actual_time}
            for activity in activities.activities]
    return service.register_actual_time_bulk(data, current_user["username"])


@router.put("/activities/multi/finish", status_code=200)
def finish_multi_activities(params: MultiFinishActivityIn,
                            db: Session = Depends(get_db),
                            current_user: dict = Depends(get_current_user)):
    """ 複数日の活動を確定する """
    service = get_time_service(db)
    data = params.dates
    return service.finish_activities(data, current_user["username"])


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
