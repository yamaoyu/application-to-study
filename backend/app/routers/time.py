import traceback
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from app.models.time_model import (
    TargetTimeIn, ActualTimeIn, RegisterActivities
)
from app.models.common_model import CheckDate, CheckYear
from db import db_model
from db.database import get_db
from lib.security import get_current_user
from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from collections import defaultdict

router = APIRouter()


def fetch_one_activity(date: str, username: str, db: Session, error_msg: str = "活動記録は未登録です"):
    activity = db.query(db_model.Activity).filter(
        db_model.Activity.date == date,
        db_model.Activity.username == username).one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail=f"{date}の{error_msg}")
    return activity


def fetch_monthly_activities(year: int, month: int, username: str, db: Session):
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    activities = db.query(db_model.Activity).filter(
        db_model.Activity.date.between(start_date, end_date),
        db_model.Activity.username == username).order_by(
            db_model.Activity.date).all()
    return activities


def fetch_one_income(year_month: str, username: str, db: Session):
    income = db.query(db_model.Income).filter(
        db_model.Income.year_month == year_month,
        db_model.Income.username == username).one_or_none()
    if not income:
        raise HTTPException(status_code=404, detail=f"{year_month}の月収は未登録です")
    return income


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


@router.get("/activities/{year}/{month}/{day}", status_code=200)
def get_day_activities(year: int,
                       month: int,
                       day: int,
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    """ 特定日の活動実績を確認する """
    try:
        CheckDate(year=year, month=month, day=day)
        date = f"{year}-{month}-{day}"
        username = current_user["username"]
        activity = fetch_one_activity(date, username, db)
        target_time = activity.target_time
        actual_time = activity.actual_time
        status = activity.status
        if status == "success":
            bonus = activity.bonus
            penalty = 0
        else:
            income = fetch_one_income(f"{year}-{month}", username, db)
            bonus = round(((income.salary / 200) * actual_time), 2)
            penalty = round(((income.salary / 200) * max((target_time - actual_time), 0)), 2)

        logger.info(f"{current_user['username']}が{date}の活動実績を取得")
        return {"date": date,
                "target_time": target_time,
                "actual_time": actual_time,
                "status": status,
                "bonus": bonus,
                "penalty": penalty}
    except HTTPException as http_e:
        raise http_e
    except ValidationError as validate_e:
        raise HTTPException(status_code=422, detail=str(validate_e.errors()[0]["ctx"]["error"]))
    except Exception:
        logger.error(f"日別の活動実績の取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/activities/{year}/{month}/{day}/target",
             status_code=201,
             response_model=RegisterActivities)
def register_target_time(target: TargetTimeIn,
                         year: int,
                         month: int,
                         day: int,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """ 目標活動時間を登録する """
    try:
        username = current_user["username"]
        target_time = target.target_time
        CheckDate(year=year, month=month, day=day)
        date = f"{year}-{month}-{day}"

        # 目標時間を登録する前に、その日の活動実績が存在するか確認
        fetch_one_income(f"{year}-{month}", username, db)

        insert_data = db_model.Activity(
            date=date, target_time=target_time, username=username)
        db.add(insert_data)
        db.commit()
        message = f"{date}の目標時間を{target_time}時間に設定しました"
        logger.info(f"{current_user['username']}が{date}の目標時間を登録")
        return {"date": date,
                "target_time": target_time,
                "actual_time": 0,
                "status": "pending",
                "message": message}
    except HTTPException as http_e:
        raise http_e
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail=f"{date}の目標時間は既に登録済みです")
    except ValidationError as validate_e:
        raise HTTPException(status_code=422, detail=str(validate_e.errors()[0]["ctx"]["error"]))
    except Exception:
        logger.error(f"目標時間の登録に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.put("/activities/{year}/{month}/{day}/actual",
            status_code=200,
            response_model=RegisterActivities)
def update_actual_time(actual: ActualTimeIn,
                       year: int,
                       month: int,
                       day: int,
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    """ 目標時間が登録済みの場合、活動時間を入力 """
    try:
        actual_time = actual.actual_time
        CheckDate(year=year, month=month, day=day)
        date = f"{year}-{month}-{day}"

        activity = fetch_one_activity(
            date, current_user["username"], db, error_msg="目標時間を先に登録してください")
        if activity.bonus == 0 and activity.penalty == 0:
            activity.actual_time = actual_time
            db.commit()
            logger.info(f"{current_user['username']}が{date}の活動時間を登録")
            return {"date": date,
                    "target_time": activity.target_time,
                    "actual_time": actual_time,
                    "status": "pending",
                    "message": f"活動時間を{actual_time}時間に設定しました"}
        else:
            raise HTTPException(status_code=400,
                                detail=f"{date}の活動実績は既に確定済みです。変更できません")
    except HTTPException as http_e:
        raise http_e
    except ValidationError as validate_e:
        raise HTTPException(status_code=422, detail=str(validate_e.errors()[0]["ctx"]["error"]))
    except Exception:
        logger.error(f"活動時間の登録に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.put("/activities/{year}/{month}/{day}/finish",
            status_code=200,
            response_model=RegisterActivities)
def finish_activity(year: int,
                    month: int,
                    day: int,
                    db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    """ 特定日の作業時間を確定し、目標を達成しているのかを確認する """
    try:
        CheckDate(year=year, month=month, day=day)
        date = f"{year}-{month}-{day}"
        username = current_user["username"]
        activity = fetch_one_activity(date, username, db)
        if activity.status != "pending":
            raise HTTPException(status_code=400, detail=f"{date}の実績は登録済みです")

        target_time = activity.target_time
        actual_time = activity.actual_time
        income = fetch_one_income(f"{year}-{month}", username, db)
        monthly_activities = fetch_monthly_activities(year, month, username, db)
        # 達成している場合はincomesテーブルのボーナスを、達成していない場合はpenaltyを加算する。
        if actual_time >= target_time:
            activity.status = "success"
            bonus = round(((income.salary / 200) * actual_time), 2)
            activity.bonus = bonus
            # 対象日のbonusをコミット
            db.commit()
            db.refresh(activity)
            # activitiesテーブルのbonusの合計を計算し、incomesテーブルに反映する
            income.total_bonus = sum([act.bonus for act in monthly_activities])
            message = f"目標達成！{bonus}万円({int(bonus * 10000)}円)ボーナス追加！"
        else:
            activity.status = "failure"
            diff = round((target_time - actual_time), 1)
            penalty = round(((income.salary / 200) * diff), 2)
            activity.penalty = penalty
            # 対象日のpenaltyをコミット
            db.commit()
            db.refresh(activity)
            # activitiesテーブルのpenaltyの合計を計算し、incomesテーブルに反映する
            income.total_penalty = sum([act.penalty for act in monthly_activities])
            message = f"{diff}時間足りませんでした。{penalty}万円({int(penalty * 10000)}円)ペナルティ追加"
        db.commit()
        logger.info(f"{current_user['username']}が{date}の活動を終了")
        return {
            "date": date,
            "target_time": target_time,
            "actual_time": actual_time,
            "status": activity.status,
            "message": message}
    except HTTPException as http_e:
        raise http_e
    except ValidationError as validate_e:
        raise HTTPException(status_code=422, detail=str(validate_e.errors()[0]["ctx"]["error"]))
    except Exception:
        logger.error(f"活動終了処理に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.get("/activities/{year}/{month}", status_code=200)
def get_month_activities(year: int,
                         month: int,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """ 特定月のデータを取得 """
    try:
        CheckDate(year=year, month=month)
        year_month = f"{year}-{month}"
        username = current_user["username"]
        activities = fetch_monthly_activities(year, month, username, db)
        if not activities:
            raise HTTPException(status_code=404,
                                detail=f"{year}年{month}月の活動は登録されていません")
        income = fetch_one_income(year_month, username, db)
        success_days = [act for act in activities if act.status == "success"]
        total_bonus = round(income.total_bonus, 2)
        total_penalty = round(income.total_penalty, 2)
        total_monthly_income = round((income.salary + total_bonus - total_penalty), 2)
        pay_adjustment = round((total_bonus - total_penalty), 2)
        logger.info(f"{current_user['username']}が{year_month}の活動実績を取得")
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
    except HTTPException as http_e:
        raise http_e
    except ValidationError as validate_e:
        raise HTTPException(status_code=422, detail=str(validate_e.errors()[0]["ctx"]["error"]))
    except Exception:
        logger.error(f"月別の活動実績の取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.get("/activities/{year:int}", status_code=200)
def get_year_activities(year: int,
                        db: Session = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    """ 特定年のデータを取得 """
    try:
        CheckYear(year=year)
        username = current_user["username"]
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        activities = db.query(db_model.Activity).filter(
            db_model.Activity.date.between(start_date, end_date),
            db_model.Activity.username == username).order_by(
                db_model.Activity.date).all()
        if not activities:
            raise HTTPException(status_code=404,
                                detail=f"{year}年の活動は登録されていません")
        incomes = db.query(db_model.Income).filter(
            db_model.Income.year_month.like(f"{year}%"),
            db_model.Income.username == username).all()
        if not incomes:
            raise HTTPException(status_code=404, detail=f"{year}年で月収が登録されている月はありません")
        success_days = sum(1 for act in activities if act.status == "success")
        fail_days = len(activities) - success_days

        total_bonus = round(sum(income.total_bonus for income in incomes), 2)
        total_penalty = round(sum(income.total_penalty for income in incomes), 2)
        salary = sum(income.salary for income in incomes)
        total_income = round((salary + total_bonus - total_penalty), 2)
        pay_adjustment = round((total_bonus - total_penalty), 2)

        monthly_info = get_month_info(activities, incomes)

        logger.info(f"{current_user['username']}が{year}年の活動実績を取得")
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
    except HTTPException as http_e:
        raise http_e
    except ValidationError as validate_e:
        raise HTTPException(status_code=422, detail=str(validate_e.errors()[0]["ctx"]["error"]))
    except Exception:
        logger.error(f"月別の活動実績の取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.get("/activities/total/", status_code=200)
def get_all_activities(db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    """ 全期間のデータを取得 """
    try:
        # 検索範囲の指定
        activities = db.query(db_model.Activity).filter(
            db_model.Activity.username == current_user["username"]).order_by(
                db_model.Activity.date).all()
        if not activities:
            raise HTTPException(status_code=404,
                                detail=f"{current_user['username']}の活動は登録されていません")
        incomes = db.query(db_model.Income).filter(
            db_model.Income.username == current_user["username"]).all()
        if not incomes:
            raise HTTPException(status_code=404,
                                detail=f"{current_user['username']}の給料は登録されていません")
        salary = round(sum([income.salary for income in incomes]), 2)
        total_bonus = round(sum([income.total_bonus for income in incomes]), 2)
        total_penalty = round(sum([income.total_penalty for income in incomes]), 2)
        pay_adjustment = round(total_bonus - total_penalty, 2)
        total_income = round((salary + total_bonus - total_penalty), 2)
        success_days = sum(1 for act in activities if act.status == "success")
        logger.info(f"{current_user['username']}が全期間の活動実績を取得")
        return {"total_income": total_income,  # 総収入(総給与 + ボーナス - ペナルティ)
                "salary": salary,  # 総給与(ベースとなる月収の合計)
                "pay_adjustment": pay_adjustment,
                "bonus": total_bonus,
                "penalty": total_penalty,
                "success_days": success_days,
                "fail_days": len(activities) - success_days}
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"月別の活動実績の取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
