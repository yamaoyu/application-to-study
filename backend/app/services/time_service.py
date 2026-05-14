from app.models.common_model import CheckDate
from datetime import datetime, date
from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from app.repositories.time_repository import TimeRepository
from app.repositories.money_repository import MoneyRepository
from app.exceptions import NotFound, BadRequest
from app.models.time_model import TargetTimeIn, ActualTimeIn
from collections import defaultdict
from lib.common import get_next_month_start


def fetch_one_activity(parsed_date: date, username: str, repo: TimeRepository, error_msg: str = "活動記録は未登録です"):
    activity = repo.get_activity_by_date_and_username(parsed_date, username)
    if not activity:
        # 0埋めしない日付を作成
        raise NotFound(
            detail=f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}の{error_msg}")
    return activity


def fetch_one_income(income_month: date, username: str, money_repo: MoneyRepository, error_msg: str = "月収は未登録です"):
    income = money_repo.get_monthly_salary(income_month, username)
    if not income:
        raise NotFound(detail=f"{income_month.year}-{income_month.month}の{error_msg}")
    return income


def fetch_monthly_activities(year: int, month: int, username: str, time_repo: TimeRepository):
    start_date = datetime(year, month, 1).date()
    end_date = get_next_month_start(start_date)
    activities = time_repo.get_monthly_activities(start_date, end_date, username)
    if not activities:
        raise NotFound(detail=f"{year}年{month}月の活動は登録されていません")
    return activities


def get_month_info(activities: list, incomes: list, summary_each_month: dict) -> dict:
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
        info["pay_adjustment"] = round((info["bonus"] - info["penalty"]), 2)

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

    def get_day_activity(self, year: int, month: int, day: int, username: str) -> dict:
        """ 特定日の活動実績を確認する """
        parsed_date = date(year, month, day)
        activity = fetch_one_activity(parsed_date, username, self.time_repo)
        income_month = date(year, month, 1)
        income = self.money_repo.get_monthly_salary(income_month, username)
        if activity.status != "pending":
            bonus = activity.bonus
            penalty = activity.penalty
        elif activity.target_time <= activity.actual_time:
            bonus = round(((income.salary / 200) * activity.actual_time), 2)
            penalty = 0
        else:
            bonus = 0
            diff = round((activity.target_time - activity.actual_time), 1)
            penalty = round(((income.salary / 200) * diff), 2)
        logger.info(f"{username}が{parsed_date.year}-{parsed_date.month}-{parsed_date.day}の活動実績を取得")
        return {"date": f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}",
                "target_time": activity.target_time,
                "actual_time": activity.actual_time,
                "status": activity.status,
                "bonus": bonus,
                "penalty": penalty}

    def get_month_activities(self, year: int, month: int, username: str) -> dict:
        activities = fetch_monthly_activities(year, month, username, self.time_repo)
        income_month = date(year, month, 1)
        income = fetch_one_income(income_month, username, self.money_repo)
        end_date = get_next_month_start(income_month)
        summary = self.time_repo.get_activity_summary(
            username, income_month, end_date)
        total_bonus = round(summary["bonus"], 2)
        total_penalty = round(summary["penalty"], 2)
        total_monthly_income = round((income.salary + total_bonus - total_penalty), 2)
        pay_adjustment = round((total_bonus - total_penalty), 2)
        logger.info(f"{username}が{income_month.year}-{income_month.month}の活動実績を取得")
        activity_list = []
        # 日付を0埋めしない形式で作成
        for act in activities:
            activity_list.append({
                "activity_id": act.activity_id,
                "date": f"{act.date.year}-{act.date.month}-{act.date.day}",
                "target_time": act.target_time,
                "actual_time": act.actual_time,
                "status": act.status,
                "bonus": act.bonus,
                "penalty": act.penalty
            })
        return {
            "total_income": total_monthly_income,
            "salary": income.salary,
            "pay_adjustment": pay_adjustment,
            "bonus": total_bonus,
            "penalty": total_penalty,
            "success_days": summary["success_days"],
            "fail_days": summary["fail_days"] + summary["pending_days"],
            "activity_list": activity_list
        }

    def get_year_activities(self, year: int, username: str) -> dict:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        activities = self.time_repo.get_yearly_activities(start_date, end_date, username)
        if not activities:
            raise NotFound(detail=f"{year}年の活動は登録されていません")
        incomes = self.money_repo.get_yearly_salaries(year, username)
        if not incomes:
            raise NotFound(detail=f"{year}年で月収が登録されている月はありません")
        summary_year = self.time_repo.get_activity_summary(
            username, start_date, end_date)

        total_bonus = round(summary_year["bonus"], 2)
        total_penalty = round(summary_year["penalty"], 2)
        salary = sum(income.salary for income in incomes)
        total_income = round((salary + total_bonus - total_penalty), 2)
        pay_adjustment = round((total_bonus - total_penalty), 2)

        summary_each_month = self.time_repo.get_monthly_activity_summary(
            username, start_date, end_date)
        monthly_info = get_month_info(activities, incomes, summary_each_month)

        logger.info(f"{username}が{year}年の活動実績を取得")
        return {
            "total_income": total_income,
            "salary": salary,
            "pay_adjustment": pay_adjustment,
            "bonus": total_bonus,
            "penalty": total_penalty,
            "success_days": summary_year["success_days"],
            "fail_days": summary_year["fail_days"] + summary_year["pending_days"],
            "monthly_info": monthly_info
        }

    def get_all_activities(self, username: str) -> dict:
        activities = self.time_repo.get_all_activities(username)
        if not activities:
            raise NotFound(detail="活動は登録されていません")
        incomes = self.money_repo.get_all_salaries(username)
        if not incomes:
            raise NotFound(detail="給料が登録されていません")
        salary = round(sum([income.salary for income in incomes]), 2)
        summary = self.time_repo.get_activity_summary(username, None, None)
        total_bonus = round(summary["bonus"], 2)
        total_penalty = round(summary["penalty"], 2)
        pay_adjustment = round(total_bonus - total_penalty, 2)
        total_income = round((salary + total_bonus - total_penalty), 2)
        success_days = summary["success_days"]
        logger.info(f"{username}が全期間の活動実績を取得")
        return {"total_income": total_income,  # 総収入(総給与 + ボーナス - ペナルティ)
                "salary": salary,  # 総給与(ベースとなる月収の合計)
                "pay_adjustment": pay_adjustment,
                "bonus": total_bonus,
                "penalty": total_penalty,
                "success_days": success_days,
                "fail_days": len(activities) - success_days}

    def get_activities_by_status(self, status: str, username: str) -> list:
        activities = self.time_repo.get_all_activities(username, status)
        if not activities:
            status_dic = {"pending": "未確定", "failure": "未達成", "success": "達成"}
            raise NotFound(detail=f"ステータスが「{status_dic[status]}」の活動は登録されていません")
        return {"activities": activities}

    def register_target_time_bulk(self, activities: list[dict], username: str):
        error_count = 0
        message = ""
        for activity in activities:
            target_time = activity["target_time"]
            date_str = activity["date"]
            try:
                # 目標時間の形式をチェック
                TargetTimeIn(target_time=target_time)
                # 日付の形式をチェック
                year, month, day = map(int, date_str.split("-"))
                CheckDate(year=year, month=month, day=day)
            except ValidationError as validate_e:
                error_count += 1
                message += f"{date_str}の活動終了に失敗:{str(validate_e.errors()[0]['ctx']['error'])}\n"
                continue
            # 目標時間を登録する前に、その日の活動実績が存在するか確認
            income_month = date(year, month, 1)
            fetch_one_income(income_month, username, self.money_repo, "月収は未登録です\n先に月収を登録してください")

            try:
                with self.time_repo.begin_nested():
                    self.time_repo.insert_target_time(date_str, target_time, username)
                    self.time_repo.flush()
                logger.info(f"{username}が複数日の目標時間を登録")
                message += f"{date_str}の目標時間を{target_time}時間に登録しました\n"
            except IntegrityError:
                error_count += 1
                message += f"{date_str}の目標時間登録に失敗: 目標時間は既に登録済みです\n"
        if error_count > 0:
            raise BadRequest(detail=message[:-1])
        return {"message": message[:-1]}

    def register_actual_time_bulk(self, params: list[dict], username: str):
        error_count = 0
        message = ""
        for param in params:
            actual_time = param["actual_time"]
            date_str = param["date"]
            try:
                # 目標時間の形式をチェック
                ActualTimeIn(actual_time=actual_time)
                # 日付の形式をチェック
                year, month, day = map(int, date_str.split("-"))
                CheckDate(year=year, month=month, day=day)
            except ValidationError as validate_e:
                error_count += 1
                message += f"{date_str}の活動時間登録に失敗:{str(validate_e.errors()[0]['ctx']['error'])}\n"
                continue
            # 目標時間を登録する前に、その日の活動実績が存在するか確認
            income_month = date(year, month, 1)
            fetch_one_income(income_month, username, self.money_repo)
            parsed_date = date(year, month, day)
            activity = fetch_one_activity(parsed_date, username, self.time_repo)

            if activity.bonus != 0 or activity.penalty != 0:
                error_count += 1
                message += f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}の活動時間登録に失敗: 既に確定されています\n"
            else:
                self.time_repo.update_actual_time(activity, actual_time)
                self.time_repo.flush()
                message += f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}の活動時間を{actual_time}時間に登録しました\n"
                logger.info(f"{username}が複数日の活動時間を登録")
        if error_count > 0:
            raise BadRequest(detail=message[:-1])
        return {"message": message[:-1]}

    def finish_activities(self, dates: list, username: str) -> dict:
        if not dates:
            raise BadRequest(detail="日付を指定してください")
        error_count = 0
        message = ""
        # まとめて終了された活動の合計を集計
        bonus_sum = 0
        penalty_sum = 0
        for date_str in dates:
            try:
                year, month, day = map(int, date_str.split("-"))
                CheckDate(year=year, month=month, day=day)
            except ValidationError as validate_e:
                error_count += 1
                message += f"{date_str}の活動終了に失敗:{str(validate_e.errors()[0]['ctx']['error'])}\n"
                continue
            parsed_date = date(year, month, day)
            activity = fetch_one_activity(parsed_date, username, self.time_repo)
            if activity.status != "pending":
                error_count += 1
                message += f"{parsed_date}の活動終了に失敗:既に確定済みです\n"
                continue
            target_time = activity.target_time
            actual_time = activity.actual_time
            income_month = date(year, month, 1)
            income = fetch_one_income(income_month, username, self.money_repo)
            # 達成している場合はincomesテーブルのボーナスを、達成していない場合はpenaltyを加算する。
            if actual_time >= target_time:
                status = "success"
                bonus = round(((income.salary / 200) * actual_time), 2)
                bonus_sum = round((bonus_sum + bonus), 2)
                penalty = 0
                message += f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}の活動を終了:ボーナス{bonus}万円({int(bonus * 10000)}円)\n"
            else:
                status = "failure"
                bonus = 0
                diff = round((target_time - actual_time), 1)
                penalty = round(((income.salary / 200) * diff), 2)
                penalty_sum = round((penalty_sum + penalty), 2)
                message += f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}の活動を終了:ペナルティ{penalty}万円({int(penalty * 10000)}円)\n"
            self.time_repo.update_activity_status_and_bonus(activity, status, bonus, penalty)
            self.time_repo.flush()
            logger.info(f"{username}が{parsed_date.year}-{parsed_date.month}-{parsed_date.day}の活動を終了")
        if error_count > 0:
            raise BadRequest(detail=message[:-1])
        pay_adjustment = round((bonus_sum - penalty_sum), 2)
        return {
            "message": message[:-1],
            "pay_adjustment": f"{pay_adjustment}万円({int(pay_adjustment * 10000)}円)",
            "total_bonus": f"{bonus_sum}万円({int(bonus_sum * 10000)}円)",
            "total_penalty": f"{penalty_sum}万円({int(penalty_sum * 10000)}円)"
        }
