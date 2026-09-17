from fastapi import APIRouter, Depends
from app.models.activity_model import (MultiTargetTimeIn,
                                       MultiActualTimeIn,
                                       ValidateStatus,
                                       getDayActivityResponse,
                                       RegisterTargetTimeResponse,
                                       RegisterActualTimeResponse,
                                       FinishActivityRequest,
                                       FinishActivityResponse,
                                       getMonthActivityResponse,
                                       getYearActivityResponse,
                                       getAllActivitiesResponse,
                                       getActivitiesByStatusResponse)
from app.models.common_model import CheckDate, CheckYearMonth, CheckYear
from db.database import get_db
from app.dependencies.auth import get_current_user
from sqlalchemy.orm import Session
from app.services.activity.register_target import RegisterTargetTimeUseCase
from app.services.activity.register_actual import RegisterActualTimeUseCase
from app.services.activity.finish_activities import FinishActivitiesUseCase
from app.services.activity.query_activities import ActivityQueryService

router = APIRouter(prefix="/activities", tags=["activities"])


def get_activity_query_service(
    db: Session = Depends(get_db),
) -> ActivityQueryService:
    return ActivityQueryService(db)


def get_register_target_time_usecase(
    db: Session = Depends(get_db),
) -> RegisterTargetTimeUseCase:
    return RegisterTargetTimeUseCase(db)


def get_register_actual_time_usecase(
    db: Session = Depends(get_db),
) -> RegisterActualTimeUseCase:
    return RegisterActualTimeUseCase(db)


def get_finish_activities_usecase(
    db: Session = Depends(get_db),
) -> FinishActivitiesUseCase:
    return FinishActivitiesUseCase(db)


@router.get("/{year}/{month}/{day}",
            status_code=200,
            response_model=getDayActivityResponse)
def get_day_activity(params: CheckDate = Depends(),
                     service: ActivityQueryService = Depends(get_activity_query_service),
                     current_user: dict = Depends(get_current_user)):
    """ 特定日の活動実績を確認する """
    # パスパラメータで受け取る年、月、日は文字列のため、intに変換する
    year = int(params.year)
    month = int(params.month)
    day = int(params.day)
    return service.get_day_activity(year, month, day, current_user["username"])


@router.post("/bulk-create-targets",
             status_code=200,
             response_model=RegisterTargetTimeResponse)
def register_multi_target_time(activities: MultiTargetTimeIn,
                               service: RegisterTargetTimeUseCase = Depends(
                                   get_register_target_time_usecase),
                               current_user: dict = Depends(get_current_user)):
    data = [{"date": activity.date, "target_time": activity.target_time}
            for activity in activities.activities]
    return service.execute(data, current_user["username"])


@router.patch("/bulk-update-actuals",
              status_code=200,
              response_model=RegisterActualTimeResponse)
def update_multi_actual_time(activities: MultiActualTimeIn,
                             service: RegisterActualTimeUseCase = Depends(
                                 get_register_actual_time_usecase),
                             current_user: dict = Depends(get_current_user)):
    """ 複数日の活動時間を登録する """
    data = [{"date": activity.date, "actual_time": activity.actual_time}
            for activity in activities.activities]
    return service.execute(data, current_user["username"])


@router.patch("/bulk-finish",
              status_code=200,
              response_model=FinishActivityResponse)
def finish_multi_activities(params: FinishActivityRequest,
                            service: FinishActivitiesUseCase = Depends(
                                get_finish_activities_usecase),
                            current_user: dict = Depends(get_current_user)):
    """ 複数日の活動を確定する """
    return service.execute(params.dates, current_user["username"])


@router.get("/{year}/{month}",
            status_code=200,
            response_model=getMonthActivityResponse)
def get_month_activities(params: CheckYearMonth = Depends(),
                         service: ActivityQueryService = Depends(get_activity_query_service),
                         current_user: dict = Depends(get_current_user)):
    """ 特定月のデータを取得 """
    return service.get_month_activities(params.year, params.month, current_user["username"])


@router.get("/{year:int}",
            status_code=200,
            response_model=getYearActivityResponse)
def get_year_activities(param: CheckYear = Depends(),
                        service: ActivityQueryService = Depends(get_activity_query_service),
                        current_user: dict = Depends(get_current_user)):
    """ 特定年のデータを取得 """
    return service.get_year_activities(param.year, current_user["username"])


@router.get("/total",
            status_code=200,
            response_model=getAllActivitiesResponse)
def get_all_activities(service: ActivityQueryService = Depends(get_activity_query_service),
                       current_user: dict = Depends(get_current_user)):
    """ 全期間を集計したデータを取得 """
    return service.get_all_activities(current_user["username"])


@router.get("",
            status_code=200,
            response_model=getActivitiesByStatusResponse)
def get_activities_by_status(param: ValidateStatus = Depends(),
                             service: ActivityQueryService = Depends(get_activity_query_service),
                             current_user: dict = Depends(get_current_user)):
    """ 日ごとの活動実績をステータスごとに取得 """
    return service.get_activities_by_status(param.status, current_user["username"])
