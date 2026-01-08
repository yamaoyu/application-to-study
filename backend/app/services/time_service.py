from app.models.common_model import CheckDate
from datetime import datetime, timedelta
from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from app.repositories.time_repository import TimeRepository
from app.repositories.money_repository import MoneyRepository
from app.exceptions import NotFound, BadRequest, Conflict
from app.models.time_model import TargetTimeIn, ActualTimeIn
from collections import defaultdict


def fetch_one_activity(date: str, username: str, repo: TimeRepository, error_msg: str = "活動記録は未登録です"):
    activity = repo.get_activity_by_date_and_username(date, username)
    if not activity:
        raise NotFound(detail=f"{date}の{error_msg}")
    return activity


def fetch_one_income(year_month: str, username: str, money_repo: MoneyRepository, error_msg: str = "月収は未登録です"):
    income = money_repo.get_monthly_salary(year_month, username)
    if not income:
        raise NotFound(detail=f"{year_month}の{error_msg}")
    return income


def fetch_monthly_activities(year: int, month: int, username: str, time_repo: TimeRepository):
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    activities = time_repo.get_monthly_activities(start_date, end_date, username)
    if not activities:
        raise NotFound(detail=f"{year}年{month}月の活動は登録されていません")
    return activities


def get_month_info(activities: list, incomes: list):
    month_dict = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
                  7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"}
    monthly_info = {}

    income_by_month = {int(income.year_month.split("-")[1]): income for income in incomes}

    activities_by_month = defaultdict(list)
    for act in activities:
        date = act.date.strftime("%Y-%m-%d")
        month = int(date.split("-")[1])
        activities_by_month[month].append(act)

    for month in range(1, 13):
        info = {}
        if month not in income_by_month:
            monthly_info[month_dict[month]] = info
            continue
        income = income_by_month[month]
        info["salary"] = income.salary
        info["bonus"] = income.total_bonus
        info["penalty"] = income.total_penalty
        info["pay_adjustment"] = round((income.total_bonus - income.total_penalty), 2)

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
        date = f"{year}-{month}-{day}"
        username = username
        activity = fetch_one_activity(date, username, self.time_repo)
        logger.info(f"{username}が{date}の活動実績を取得")
        return {"date": date,
                "target_time": activity.target_time,
                "actual_time": activity.actual_time,
                "status": activity.status,
                "bonus": activity.bonus,
                "penalty": activity.penalty}

    def get_month_activities(self, year: int, month: int, username: str) -> dict:
        year_month = f"{year}-{month}"
        activities = fetch_monthly_activities(year, month, username, self.time_repo)
        income = fetch_one_income(year_month, username, self.money_repo)
        success_days = [act for act in activities if act.status == "success"]
        total_bonus = round(income.total_bonus, 2)
        total_penalty = round(income.total_penalty, 2)
        total_monthly_income = round((income.salary + total_bonus - total_penalty), 2)
        pay_adjustment = round((total_bonus - total_penalty), 2)
        logger.info(f"{username}が{year_month}の活動実績を取得")
        return {
            "total_income": total_monthly_income,
            "salary": income.salary,
            "pay_adjustment": pay_adjustment,
            "bonus": total_bonus,
            "penalty": total_penalty,
            "success_days": len(success_days),
            "fail_days": len(activities) - len(success_days),
            "activity_list": activities
        }

    def get_year_activities(self, year: int, username: str) -> dict:
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        activities = self.time_repo.get_yearly_activities(start_date, end_date, username)
        if not activities:
            raise NotFound(detail=f"{year}年の活動は登録されていません")
        incomes = self.money_repo.get_yearly_salaries(year, username)
        if not incomes:
            raise NotFound(detail=f"{year}年で月収が登録されている月はありません")
        success_days = sum(1 for act in activities if act.status == "success")
        fail_days = len(activities) - success_days

        total_bonus = round(sum(income.total_bonus for income in incomes), 2)
        total_penalty = round(sum(income.total_penalty for income in incomes), 2)
        salary = sum(income.salary for income in incomes)
        total_income = round((salary + total_bonus - total_penalty), 2)
        pay_adjustment = round((total_bonus - total_penalty), 2)

        monthly_info = get_month_info(activities, incomes)

        logger.info(f"{username}が{year}年の活動実績を取得")
        return {
            "total_income": total_income,
            "salary": salary,
            "pay_adjustment": pay_adjustment,
            "bonus": total_bonus,
            "penalty": total_penalty,
            "success_days": success_days,
            "fail_days": fail_days,
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
        total_bonus = round(sum([income.total_bonus for income in incomes]), 2)
        total_penalty = round(sum([income.total_penalty for income in incomes]), 2)
        pay_adjustment = round(total_bonus - total_penalty, 2)
        total_income = round((salary + total_bonus - total_penalty), 2)
        success_days = sum(1 for act in activities if act.status == "success")
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

    def register_target_time(self, target_time: float, year: int, month: int, day: int, username: str) -> None:
        date = f"{year}-{month}-{day}"
        # 目標時間を登録する前に、その月の月収が存在するか確認
        fetch_one_income(f"{year}-{month}", username, self.money_repo)
        try:
            self.time_repo.insert_target_time(date, target_time, username)
            self.time_repo.flush()
        except IntegrityError:
            raise Conflict(detail=f"{date}の目標時間は既に登録済みです")
        message = f"{date}の目標時間を{target_time}時間に設定しました"
        logger.info(f"{username}が{date}の目標時間を登録")
        return {
            "date": date,
            "target_time": target_time,
            "actual_time": 0,
            "status": "pending",
            "message": message
        }

    def register_target_time_bulk(self, activities: list[dict], username: str):
        error_count = 0
        message = ""
        for activity in activities:
            username = username
            target_time = activity["target_time"]
            date = activity["date"]
            try:
                # 目標時間の形式をチェック
                TargetTimeIn(target_time=target_time)
                # 日付の形式をチェック
                year, month, day = map(int, date.split("-"))
                CheckDate(year=year, month=month, day=day)
            except ValidationError as validate_e:
                error_count += 1
                message += f"{date}の活動終了に失敗:{str(validate_e.errors()[0]['ctx']['error'])}\n"
                continue
            # 目標時間を登録する前に、その日の活動実績が存在するか確認
            year_month = f"{year}-{month}"
            fetch_one_income(year_month, username, self.money_repo, "月収は未登録です\n先に月収を登録してください")

            try:
                with self.time_repo.begin_nested():
                    self.time_repo.insert_target_time(date, target_time, username)
                    self.time_repo.flush()
                logger.info(f"{username}が複数日の目標時間を登録")
                message += f"{date}の目標時間を{target_time}時間に登録しました\n"
            except IntegrityError:
                error_count += 1
                message += f"{date}の目標時間登録に失敗: 目標時間は既に登録済みです\n"
        if error_count > 0:
            raise BadRequest(detail=message[:-1])
        return {"message": message[:-1]}

    def register_actual_time(self, actual_time: float, year: int, month: int, day: int, username: str) -> None:
        date = f"{year}-{month}-{day}"
        activity = fetch_one_activity(
            date, username, self.time_repo, error_msg="目標時間を先に登録してください")
        if activity.bonus == 0 and activity.penalty == 0:
            self.time_repo.update_actual_time(activity, actual_time)
            self.time_repo.flush()
            message = f"{date}の活動時間を{actual_time}時間に設定しました"
            logger.info(f"{username}が{date}の活動時間を登録")
            return {"date": date,
                    "target_time": activity.target_time,
                    "actual_time": actual_time,
                    "status": "pending",
                    "message": message}
        else:
            raise Conflict(detail=f"{date}の活動実績は既に確定済みです。変更できません")

    def register_actual_time_bulk(self, params: list[dict], username: str):
        error_count = 0
        message = ""
        for param in params:
            username = username
            actual_time = param["actual_time"]
            date = param["date"]
            # 目標時間の形式をチェック
            ActualTimeIn(actual_time=actual_time)
            # 日付の形式をチェック
            year, month, day = map(int, date.split("-"))
            try:
                CheckDate(year=year, month=month, day=day)
            except ValidationError as validate_e:
                error_count += 1
                message += f"{date}の活動時間登録に失敗:{str(validate_e.errors()[0]['ctx']['error'])}\n"
                continue
            # 目標時間を登録する前に、その日の活動実績が存在するか確認
            year_month = f"{year}-{month}"
            fetch_one_income(year_month, username, self.money_repo)
            activity = fetch_one_activity(date, username, self.time_repo)

            if activity.bonus != 0 or activity.penalty != 0:
                error_count += 1
                message += f"{date}の活動時間登録に失敗: 既に確定されています\n"
            else:
                self.time_repo.update_actual_time(activity, actual_time)
                self.time_repo.flush()
                message += f"{date}の活動時間を{actual_time}時間に登録しました\n"
                logger.info(f"{username}が複数日の活動時間を登録")
        if error_count > 0:
            raise BadRequest(detail=message[:-1])
        return {"message": message[:-1]}

    def finish_activity(self, year: int, month: int, day: int, username: str) -> None:
        date = f"{year}-{month}-{day}"
        activity = fetch_one_activity(date, username, self.time_repo)
        if activity.status != "pending":
            raise Conflict(detail=f"{date}の実績は登録済みです")
        # 達成している場合はincomesテーブルのボーナスを、達成していない場合はpenaltyを加算する。
        target_time = activity.target_time
        actual_time = activity.actual_time
        income = fetch_one_income(f"{year}-{month}", username, self.money_repo)
        monthly_activities = fetch_monthly_activities(year, month, username, self.time_repo)
        if actual_time >= target_time:
            status = "success"
            bonus = round(((income.salary / 200) * actual_time), 2)
            penalty = 0
            total_bonus = sum([act.bonus for act in monthly_activities]) + bonus
            total_penalty = income.total_penalty
            message = f"目標達成！{bonus}万円({int(bonus * 10000)}円)ボーナス追加！"
        else:
            status = "failure"
            bonus = 0
            diff = round((target_time - actual_time), 1)
            penalty = round(((income.salary / 200) * diff), 2)
            total_bonus = income.total_bonus
            total_penalty = sum([act.penalty for act in monthly_activities]) + penalty
            message = f"{diff}時間足りませんでした。{penalty}万円({int(penalty * 10000)}円)ペナルティ追加"
        self.time_repo.update_activity_status_and_bonus(activity, status, bonus, penalty)
        self.money_repo.update_bonus_and_penalty(income, total_bonus, total_penalty)
        self.time_repo.flush()
        logger.info(f"{username}が{date}の活動を終了")
        return {
            "date": date,
            "target_time": target_time,
            "actual_time": actual_time,
            "status": status,
            "message": message}

    def finish_activities(self, dates: list, username: str) -> dict:
        error_count = 0
        message = ""
        # まとめて終了された活動の合計を集計
        pay_adjustment = 0
        bonus_sum = 0
        penalty_sum = 0
        if len(dates) == 0:
            raise BadRequest(detail="日付を指定してください")
        for date in dates:
            year, month, day = map(int, date.split("-"))
            try:
                CheckDate(year=year, month=month, day=day)
            except ValidationError as validate_e:
                error_count += 1
                message += f"{date}の活動終了に失敗:{str(validate_e.errors()[0]['ctx']['error'])}\n"
                continue
            date = f"{year}-{month}-{day}"
            username = username
            activity = fetch_one_activity(date, username, self.time_repo)
            if activity.status != "pending":
                error_count += 1
                message += f"{date}の活動終了に失敗:既に確定済みです\n"
                continue
            target_time = activity.target_time
            actual_time = activity.actual_time
            income = fetch_one_income(f"{year}-{month}", username, self.money_repo)
            monthly_activities = fetch_monthly_activities(year, month, username, self.time_repo)
            # 達成している場合はincomesテーブルのボーナスを、達成していない場合はpenaltyを加算する。
            if actual_time >= target_time:
                status = "success"
                bonus = round(((income.salary / 200) * actual_time), 2)
                bonus_sum = round((bonus_sum + bonus), 2)
                penalty = 0
                total_bonus = sum([act.bonus for act in monthly_activities]) + bonus
                total_penalty = income.total_penalty
                message += f"{date}の活動を終了:ボーナス{bonus}万円({int(bonus * 10000)}円)\n"
            else:
                status = "failure"
                bonus = 0
                diff = round((target_time - actual_time), 1)
                penalty = round(((income.salary / 200) * diff), 2)
                penalty_sum = round((penalty_sum + penalty), 2)
                total_bonus = income.total_bonus
                total_penalty = sum([act.penalty for act in monthly_activities]) + penalty
                message += f"{date}の活動を終了:ペナルティ{penalty}万円({int(penalty * 10000)}円)\n"
            self.time_repo.update_activity_status_and_bonus(activity, status, bonus, penalty)
            self.money_repo.update_bonus_and_penalty(income, total_bonus, total_penalty)
            self.time_repo.flush()
            logger.info(f"{username}が{date}の活動を終了")
        if error_count > 0:
            raise BadRequest(detail=message[:-1])
        pay_adjustment = pay_adjustment = round((bonus_sum - penalty_sum), 2)
        return {
            "message": message[:-1],
            "pay_adjustment": f"{pay_adjustment}万円({int(pay_adjustment * 10000)}円)",
            "total_bonus": f"{bonus_sum}万円({int(bonus_sum * 10000)}円)",
            "total_penalty": f"{penalty_sum}万円({int(penalty_sum * 10000)}円)"
        }
