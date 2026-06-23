from datetime import datetime, date
from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.time_repository import TimeRepository
from app.repositories.money_repository import MoneyRepository
from app.exceptions import NotFound, BulkOperationFailed
from collections import defaultdict
from lib.common import get_next_month_start
from app.domain.activity_calculator import calc_bonus_penalty, calc_activity_result, round_money
from app.models.time_model import (getDayActivityResponse,
                                   RegisterTargetTimeResponse,
                                   RegisterActualTimeResponse,
                                   FinishActivityResponse,
                                   getMonthActivityResponse,
                                   getYearActivityResponse,
                                   getAllActivitiesResponse,
                                   getActivitiesByStatusResponse,
                                   MonthlyInfo,
                                   Status)
from typing import Optional
from db import db_model
from app.error_codes import NotFoundCode, BadRequestCode, ConflictCode


def fetch_one_activity(parsed_date: date,
                       username: str,
                       repo: TimeRepository
                       ) -> Optional[db_model.Activity]:
    return repo.get_activity_by_date_and_username(parsed_date, username)


def fetch_one_income(income_month: date,
                     username: str,
                     money_repo: MoneyRepository
                     ) -> Optional[db_model.Activity]:
    return money_repo.get_monthly_salary(income_month, username)


def fetch_monthly_activities(year: int,
                             month: int,
                             username: str,
                             time_repo: TimeRepository
                             ) -> list[db_model.Activity]:
    start_date = datetime(year, month, 1).date()
    end_date = get_next_month_start(start_date)
    activities = time_repo.get_monthly_activities(start_date, end_date, username)
    if not activities:
        raise NotFound(code=NotFoundCode.ACTIVITY_NOT_FOUND)
    return activities


def get_month_info(activities: list,
                   incomes: list,
                   summary_each_month: list
                   ) -> dict[str, Optional[MonthlyInfo]]:
    month_dict = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
                  7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"}
    monthly_info = {}

    income_by_month = {income.income_month.month: income for income in incomes}

    activities_by_month = defaultdict(list)
    for act in activities:
        date = act.date.strftime("%Y-%m-%d")
        month = int(date.split("-")[1])
        activities_by_month[month].append(act)

    summary = {
        int(row.month): {
            "success_days": row.success_days,
            "fail_days": row.fail_days,
            "bonus": round(row.bonus, 2),
            "penalty": round(row.penalty, 2),
            "pay_adjustment": round(row.bonus - row.penalty, 2),
        }
        for row in summary_each_month
    }

    for month in range(1, 13):
        info = {}
        if month not in income_by_month:
            monthly_info[month_dict[month]] = info
            continue
        income = income_by_month[month]
        summary_by_month = summary.get(month, {
            "success_days": 0,
            "fail_days": 0,
            "bonus": 0.0,
            "penalty": 0.0,
            "pay_adjustment": 0.0,
        })
        info["salary"] = income.salary
        info["bonus"] = summary_by_month["bonus"]
        info["penalty"] = summary_by_month["penalty"]
        info["pay_adjustment"] = round_money(info["bonus"] - info["penalty"])
        info["total_income"] = round_money(info["salary"] + info["bonus"] - info["penalty"])

        if month in activities_by_month:
            success_days = sum(1 for act in activities_by_month[month] if act.status == "success")
            info["success_days"] = success_days
            info["fail_days"] = len(activities_by_month[month]) - success_days
        else:
            info["success_days"] = 0
            info["fail_days"] = 0

        monthly_info[month_dict[month]] = info
    return monthly_info


class TimeService():
    def __init__(self, db: Session) -> None:
        self.time_repo = TimeRepository(db)
        self.money_repo = MoneyRepository(db)

    def get_day_activity(self,
                         year: int,
                         month: int,
                         day: int,
                         username: str
                         ) -> getDayActivityResponse:
        """ 特定日の活動実績を確認する """
        parsed_date = date(year, month, day)
        activity = fetch_one_activity(parsed_date, username, self.time_repo)
        if not activity:
            raise NotFound(code=NotFoundCode.ACTIVITY_NOT_FOUND)
        income_month = date(year, month, 1)
        income = fetch_one_income(income_month, username, self.money_repo)
        if not income:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND_ERROR)
        if activity.status != "pending":
            bonus = activity.bonus
            penalty = activity.penalty
        else:
            adjustment = calc_bonus_penalty(
                income.salary, activity.target_time, activity.actual_time)
            bonus = adjustment.bonus
            penalty = adjustment.penalty
        logger.info(f"{username}が{parsed_date.year}-{parsed_date.month}-{parsed_date.day}の活動実績を取得")
        return getDayActivityResponse(
            activity_id=activity.activity_id,
            date=f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}",
            target_time=activity.target_time,
            actual_time=activity.actual_time,
            status=Status(activity.status),
            bonus=bonus,
            penalty=penalty
        )

    def get_month_activities(self,
                             year: int,
                             month: int,
                             username: str
                             ) -> getMonthActivityResponse:
        activities = fetch_monthly_activities(year, month, username, self.time_repo)
        income_month = date(year, month, 1)
        income = fetch_one_income(income_month, username, self.money_repo)
        if not income:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND_ERROR)
        end_date = get_next_month_start(income_month)
        summary = self.time_repo.get_activity_summary(
            username, income_month, end_date)
        total_bonus = round_money(summary["bonus"])
        total_penalty = round_money(summary["penalty"])
        total_monthly_income = round_money(income.salary + total_bonus - total_penalty)
        pay_adjustment = round_money(total_bonus - total_penalty)
        logger.info(f"{username}が{income_month.year}-{income_month.month}の活動実績を取得")
        activity_list = []
        # 日付を0埋めしない形式で作成
        for act in activities:
            activity_list.append({
                "date": f"{act.date.year}-{act.date.month}-{act.date.day}",
                "target_time": act.target_time,
                "actual_time": act.actual_time,
                "status": act.status,
                "bonus": act.bonus,
                "penalty": act.penalty
            })
        return getMonthActivityResponse(
            total_income=total_monthly_income,
            salary=income.salary,
            pay_adjustment=pay_adjustment,
            bonus=total_bonus,
            penalty=total_penalty,
            success_days=summary["success_days"],
            fail_days=summary["fail_days"] + summary["pending_days"],
            activity_list=activity_list
        )

    def get_year_activities(self,
                            year: int,
                            username: str
                            ) -> getYearActivityResponse:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        activities = self.time_repo.get_yearly_activities(start_date, end_date, username)
        if not activities:
            raise NotFound(code=NotFoundCode.ACTIVITY_NOT_FOUND)
        incomes = self.money_repo.get_yearly_salaries(year, username)
        if not incomes:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND_ERROR)
        summary_year = self.time_repo.get_activity_summary(
            username, start_date, end_date)

        total_bonus = round_money(summary_year["bonus"])
        total_penalty = round_money(summary_year["penalty"])
        salary = round_money(sum(income.salary for income in incomes))
        total_income = round_money(salary + total_bonus - total_penalty)
        pay_adjustment = round_money(total_bonus - total_penalty)

        summary_each_month = self.time_repo.get_monthly_activity_summary(
            username, start_date, end_date)
        monthly_info = get_month_info(activities, incomes, summary_each_month)

        logger.info(f"{username}が{year}年の活動実績を取得")
        return getYearActivityResponse(
            total_income=total_income,
            salary=salary,
            pay_adjustment=pay_adjustment,
            bonus=total_bonus,
            penalty=total_penalty,
            success_days=summary_year["success_days"],
            fail_days=summary_year["fail_days"] + summary_year["pending_days"],
            monthly_info=monthly_info
        )

    def get_all_activities(self, username: str) -> getAllActivitiesResponse:
        activities = self.time_repo.get_all_activities(username)
        if not activities:
            raise NotFound(code=NotFoundCode.ACTIVITY_NOT_FOUND)
        incomes = self.money_repo.get_all_salaries(username)
        if not incomes:
            raise NotFound(code=NotFoundCode.SALARY_NOT_FOUND_ERROR)
        salary = round_money(sum([income.salary for income in incomes]))
        summary = self.time_repo.get_activity_summary(username, None, None)
        total_bonus = round_money(summary["bonus"])
        total_penalty = round_money(summary["penalty"])
        pay_adjustment = round_money(total_bonus - total_penalty)
        total_income = round_money(salary + total_bonus - total_penalty)
        success_days = summary["success_days"]
        logger.info(f"{username}が全期間の活動実績を取得")
        return getAllActivitiesResponse(
            total_income=total_income,
            salary=salary,
            pay_adjustment=pay_adjustment,
            bonus=total_bonus,
            penalty=total_penalty,
            success_days=success_days,
            fail_days=len(activities) - success_days
        )

    def get_activities_by_status(self,
                                 status: str,
                                 username: str
                                 ) -> getActivitiesByStatusResponse:
        activities = self.time_repo.get_all_activities(username, status)
        if not activities:
            raise NotFound(code=NotFoundCode.ACTIVITY_NOT_FOUND)
        return getActivitiesByStatusResponse(activities=[
            getDayActivityResponse(
                activity_id=act.activity_id,
                date=f"{act.date.year}-{act.date.month}-{act.date.day}",
                target_time=act.target_time,
                actual_time=act.actual_time,
                status=Status(act.status),
                bonus=act.bonus,
                penalty=act.penalty
            ) for act in activities
        ])

    def register_target_time_bulk(self,
                                  activities: list[dict],
                                  username: str
                                  ) -> RegisterTargetTimeResponse:
        results = []
        error_count = 0
        for activity in activities:
            target_time = activity["target_time"]
            date_str = activity["date"]
            year, month, day = map(int, date_str.split("-"))
            # 目標時間を登録する前に、その日の活動実績が存在するか確認
            income_month = date(year, month, 1)
            income = fetch_one_income(income_month, username, self.money_repo)
            if not income:
                results.append({
                    "date": f"{year}-{month}-{day}",
                    "result": "error",
                    "reason": NotFoundCode.SALARY_NOT_FOUND_ERROR,
                    "target_time": None
                })
                error_count += 1
                continue
            try:
                with self.time_repo.begin_nested():
                    parsed_date = date(year, month, day)
                    self.time_repo.insert_target_time(parsed_date, target_time, username)
                    self.time_repo.flush()
                logger.info(f"{username}が複数日の目標時間を登録")
                results.append({
                    "date": f"{year}-{month}-{day}",
                    "result": "success",
                    "target_time": target_time,
                    "reason": None
                })
            except IntegrityError:
                results.append({
                    "date": f"{year}-{month}-{day}",
                    "result": "error",
                    "reason": ConflictCode.TARGET_TIME_ALREADY_REGISTERED,
                    "target_time": None
                })
                error_count += 1
            except Exception as e:
                results.append({
                    "date": f"{year}-{month}-{day}",
                    "result": "error",
                    "reason": BadRequestCode.UNEXPECTED_ERROR,
                    "target_time": None
                })
                error_count += 1
                logger.error(f"Error registering target time for {date_str}: {str(e)}")
        if error_count == len(activities):
            raise BulkOperationFailed(results=results, code=BadRequestCode.BULK_OPERATION_FAILED)
        return RegisterTargetTimeResponse(results=results)

    def register_actual_time_bulk(self,
                                  params: list[dict],
                                  username: str
                                  ) -> RegisterActualTimeResponse:
        results = []
        error_count = 0
        for param in params:
            actual_time = param["actual_time"]
            date_str = param["date"]
            year, month, day = map(int, date_str.split("-"))
            # 目標時間を登録する前に、その日の活動実績が存在するか確認
            income_month = date(year, month, 1)
            income = fetch_one_income(income_month, username, self.money_repo)
            if not income:
                results.append({
                    "date": f"{year}-{month}-{day}",
                    "result": "error",
                    "reason": NotFoundCode.SALARY_NOT_FOUND_ERROR,
                    "actual_time": None
                })
                error_count += 1
                continue
            try:
                parsed_date = date(year, month, day)
                activity = fetch_one_activity(parsed_date, username, self.time_repo)
                if not activity:
                    results.append({
                        "date": f"{year}-{month}-{day}",
                        "result": "error",
                        "reason": NotFoundCode.ACTIVITY_NOT_FOUND,
                        "actual_time": None
                    })
                    error_count += 1
                    continue
                if activity.status != "pending":
                    results.append({
                        "date": f"{year}-{month}-{day}",
                        "result": "error",
                        "reason": ConflictCode.ACTIVITY_ALREADY_FINISHED,
                        "actual_time": None
                    })
                    error_count += 1
                else:
                    with self.time_repo.begin_nested():
                        self.time_repo.update_actual_time(activity, actual_time)
                        self.time_repo.flush()
                    results.append({
                        "date": f"{year}-{month}-{day}",
                        "result": "success",
                        "actual_time": actual_time,
                        "reason": None
                    })
                    logger.info(f"{username}が複数日の活動時間を登録")
            except Exception as e:
                results.append({
                    "date": f"{year}-{month}-{day}",
                    "result": "error",
                    "reason": BadRequestCode.UNEXPECTED_ERROR,
                    "actual_time": None
                })
                error_count += 1
                logger.error(f"Error registering actual time for {date_str}: {str(e)}")
        if error_count == len(params):
            raise BulkOperationFailed(results=results, code=BadRequestCode.BULK_OPERATION_FAILED)
        return RegisterActualTimeResponse(results=results)

    def finish_activities(self,
                          dates: list,
                          username: str
                          ) -> FinishActivityResponse:
        # まとめて終了された活動の合計を集計
        bonus_sum = 0
        penalty_sum = 0
        results = []
        error_count = 0
        for date_str in dates:
            year, month, day = map(int, date_str.split("-"))
            parsed_date = date(year, month, day)
            activity = fetch_one_activity(parsed_date, username, self.time_repo)
            if not activity:
                results.append({
                    "date": f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}",
                    "reason": NotFoundCode.ACTIVITY_NOT_FOUND,
                    "result": "error",
                    "bonus": None,
                    "penalty": None,
                    "status": None
                })
                error_count += 1
                continue
            if activity.status != "pending":
                results.append({
                    "date": f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}",
                    "reason": ConflictCode.ACTIVITY_ALREADY_FINISHED,
                    "result": "error",
                    "bonus": None,
                    "penalty": None,
                    "status": None
                })
                error_count += 1
                continue
            target_time = activity.target_time
            actual_time = activity.actual_time
            income_month = date(year, month, 1)
            income = fetch_one_income(income_month, username, self.money_repo)
            if not income:
                results.append({
                    "date": f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}",
                    "reason": NotFoundCode.SALARY_NOT_FOUND_ERROR,
                    "result": "error",
                    "bonus": None,
                    "penalty": None,
                    "status": None
                })
                error_count += 1
                continue
            try:
                # 達成している場合はincomesテーブルのボーナスを、達成していない場合はpenaltyを加算する。
                activity_result = calc_activity_result(income.salary, target_time, actual_time)
                bonus = activity_result.bonus
                penalty = activity_result.penalty
                status = activity_result.status
                bonus_sum += bonus
                penalty_sum += penalty
                with self.time_repo.begin_nested():
                    self.time_repo.update_activity_status_and_bonus(
                        activity, status, bonus, penalty)
                    self.time_repo.flush()
                    logger.info(
                        f"{username}が{parsed_date.year}-{parsed_date.month}-{parsed_date.day}の活動を終了")
                result = {
                    "date": f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}",
                    "status": status,
                    "bonus": bonus,
                    "penalty": penalty,
                    "result": "success",
                    "reason": None
                }
                results.append(result)
            except Exception as e:
                results.append({
                    "date": f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}",
                    "reason": BadRequestCode.UNEXPECTED_ERROR,
                    "result": "error",
                    "bonus": None,
                    "penalty": None,
                    "status": None
                })
                error_count += 1
                logger.error(f"Error finishing activity for {date_str}: {str(e)}")
        if error_count == len(dates):
            raise BulkOperationFailed(results=results, code=BadRequestCode.BULK_OPERATION_FAILED)
        return FinishActivityResponse(pay_adjustment=round_money(bonus_sum - penalty_sum),
                                      total_bonus=round_money(bonus_sum),
                                      total_penalty=round_money(penalty_sum),
                                      results=results)
