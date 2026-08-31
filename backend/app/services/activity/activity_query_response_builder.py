from datetime import date
from collections import defaultdict
from typing import Optional
from app.models.activity_model import (getDayActivityResponse,
                                       getMonthActivityResponse,
                                       getYearActivityResponse,
                                       getAllActivitiesResponse,
                                       getActivitiesByStatusResponse,
                                       Status,
                                       MonthlyInfo)
from app.domain.activity.activity import Activity
from app.domain.activity.adjustment import Adjustment
from app.services.activity.utils import format_date
from app.domain.money.amount import round_money_amount


def _build_month_info(activities: list,
                      incomes: list,
                      summary_each_month: dict
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

    for month in range(1, 13):
        month_key = month_dict[month]
        if month not in income_by_month:
            monthly_info[month_key] = {}
            continue
        income = income_by_month[month]
        summary_by_month = summary_each_month.get(month, {
            "success_days": 0,
            "fail_days": 0,
            "bonus": 0.0,
            "penalty": 0.0,
            "pay_adjustment": 0.0,
        })

        monthly_info[month_key] = {
            "salary": income.salary,
            "bonus": summary_by_month["bonus"],
            "penalty": summary_by_month["penalty"],
            "pay_adjustment": summary_by_month["pay_adjustment"],
            "total_income": round_money_amount(income.salary + summary_by_month["bonus"] + summary_by_month["penalty"]),
            "success_days": summary_by_month["success_days"],
            "fail_days": summary_by_month["fail_days"]
        }
    return monthly_info


class ActivityResponseBuilder():
    @staticmethod
    def build_day_activity_response(activity_id: int, activity: Activity, adjustment: Adjustment, activity_date: date) -> getDayActivityResponse:
        return getDayActivityResponse(
            activity_id=activity_id,
            date=format_date(activity_date),
            target_time=activity.target_time,
            actual_time=activity.actual_time,
            status=Status(activity.status),
            bonus=adjustment.bonus,
            penalty=adjustment.penalty
        )

    @staticmethod
    def build_month_activities_response(summary: dict, activities: list, salary: float) -> getMonthActivityResponse:
        total_bonus = round_money_amount(summary["bonus"])
        total_penalty = round_money_amount(summary["penalty"])
        total_monthly_income = round_money_amount(salary + total_bonus - total_penalty)
        pay_adjustment = round_money_amount(total_bonus - total_penalty)
        activity_list = []
        # 日付を0埋めしない形式で作成
        for act in activities:
            activity_list.append({
                "date": format_date(act.date),
                "target_time": act.target_time,
                "actual_time": act.actual_time,
                "status": act.status,
                "bonus": act.bonus,
                "penalty": act.penalty
            })
        return getMonthActivityResponse(
            total_income=total_monthly_income,
            salary=salary,
            pay_adjustment=pay_adjustment,
            bonus=total_bonus,
            penalty=total_penalty,
            success_days=summary["success_days"],
            fail_days=summary["fail_days"] + summary["pending_days"],
            activity_list=activity_list
        )

    @staticmethod
    def build_year_activities_response(
        summary_year: dict,
        incomes: list,
        summary_each_month: dict,
        activities: list
    ) -> getYearActivityResponse:
        salary = round_money_amount(sum(income.salary for income in incomes))
        total_bonus = round_money_amount(summary_year["bonus"])
        total_penalty = round_money_amount(summary_year["penalty"])
        total_income = round_money_amount(salary + total_bonus - total_penalty)
        pay_adjustment = round_money_amount(total_bonus - total_penalty)
        monthly_info = _build_month_info(activities, incomes, summary_each_month)

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

    @staticmethod
    def build_all_activities_response(summary: dict, salary: float, activity_count: int) -> getAllActivitiesResponse:
        total_bonus = round_money_amount(summary["bonus"])
        total_penalty = round_money_amount(summary["penalty"])
        pay_adjustment = round_money_amount(total_bonus - total_penalty)
        total_income = round_money_amount(salary + total_bonus - total_penalty)
        success_days = summary["success_days"]

        return getAllActivitiesResponse(
            total_income=total_income,
            salary=salary,
            pay_adjustment=pay_adjustment,
            bonus=total_bonus,
            penalty=total_penalty,
            success_days=success_days,
            fail_days=activity_count - success_days
        )

    @staticmethod
    def build_activities_by_status_response(activities: list) -> getActivitiesByStatusResponse:
        return getActivitiesByStatusResponse(activities=[
            getDayActivityResponse(
                activity_id=act.activity_id,
                date=format_date(act.date),
                target_time=act.target_time,
                actual_time=act.actual_time,
                status=Status(act.status),
                bonus=act.bonus,
                penalty=act.penalty
            ) for act in activities
        ])
