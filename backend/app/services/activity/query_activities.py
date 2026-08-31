from datetime import date
from lib.log_conf import logger
from sqlalchemy.orm import Session
from app.repositories.activity_repository import ActivityRepository
from app.repositories.money_repository import MoneyRepository
from app.exceptions import NotFound
from lib.common import get_month_end
from app.models.activity_model import (getDayActivityResponse,
                                       getMonthActivityResponse,
                                       getYearActivityResponse,
                                       getAllActivitiesResponse,
                                       getActivitiesByStatusResponse)
from app.error_codes import NotFoundCode
from app.domain.money.amount import round_money_amount
from app.domain.income.monthly_income import MonthlySalary
from app.domain.activity.adjustment import Adjustment
from app.domain.activity.activity import Activity, ActivityStatus
from app.services.activity.activity_query_response_builder import ActivityResponseBuilder


class ActivityQueryService():
    def __init__(self, db: Session) -> None:
        self.time_repo = ActivityRepository(db)
        self.money_repo = MoneyRepository(db)

    def get_day_activity(self,
                         year: int,
                         month: int,
                         day: int,
                         username: str
                         ) -> getDayActivityResponse:
        """ 特定日の活動実績を確認する """
        activity_date = date(year, month, day)
        activity_row = self.time_repo.get_activity_by_date_and_username(activity_date, username)
        if not activity_row:
            raise NotFound(code=NotFoundCode.ACTIVITY_NOT_FOUND)
        income_month = date(year, month, 1)
        income_row = self.money_repo.get_monthly_salary(income_month, username)
        if not income_row:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND)
        activity = Activity(
            target_time=activity_row.target_time,
            actual_time=activity_row.actual_time,
            status=ActivityStatus(activity_row.status),
            adjustment=Adjustment(bonus=activity_row.bonus, penalty=activity_row.penalty)
        )
        monthly_salary = MonthlySalary(income_row.salary)
        adjustment = activity.effective_adjustment(monthly_salary)
        logger.info(
            f"{username}が{activity_date.year}-{activity_date.month}-{activity_date.day}の活動実績を取得")
        return ActivityResponseBuilder.build_day_activity_response(
            activity_row.activity_id, activity, adjustment, activity_date
        )

    def get_month_activities(self,
                             year: int,
                             month: int,
                             username: str
                             ) -> getMonthActivityResponse:
        start_date = date(year, month, 1)
        income_row = self.money_repo.get_monthly_salary(start_date, username)
        if not income_row:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND)
        end_date = get_month_end(start_date)
        summary = self.time_repo.get_activity_summary(
            username, start_date, end_date)

        activities = self.time_repo.get_monthly_activities(start_date, end_date, username)

        logger.info(f"{username}が{start_date.year}-{start_date.month}の活動実績を取得")
        return ActivityResponseBuilder.build_month_activities_response(summary, activities, income_row.salary)

    def get_year_activities(self,
                            year: int,
                            username: str
                            ) -> getYearActivityResponse:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        incomes = self.money_repo.get_yearly_salaries(year, username)
        if not incomes:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND)

        summary_year = self.time_repo.get_activity_summary(
            username, start_date, end_date)
        summary_each_month = self.time_repo.get_monthly_activity_summary(
            username, start_date, end_date)

        activities = self.time_repo.get_yearly_activities(start_date, end_date, username)
        logger.info(f"{username}が{year}年の活動実績を取得")

        return ActivityResponseBuilder.build_year_activities_response(summary_year, incomes, summary_each_month, activities)

    def get_all_activities(self, username: str) -> getAllActivitiesResponse:
        incomes = self.money_repo.get_all_salaries(username)
        if not incomes:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND)
        salary = round_money_amount(sum([income.salary for income in incomes]))

        summary = self.time_repo.get_activity_summary(username, None, None)
        activity_count = self.time_repo.count_all_activities(username)

        logger.info(f"{username}が全期間の活動実績を取得")
        return ActivityResponseBuilder.build_all_activities_response(summary, salary, activity_count)

    def get_activities_by_status(self,
                                 status: str,
                                 username: str
                                 ) -> getActivitiesByStatusResponse:
        activities = self.time_repo.get_all_activities(username, status)
        return ActivityResponseBuilder.build_activities_by_status_response(activities)
