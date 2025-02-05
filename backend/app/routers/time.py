import traceback
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from app.models.time_model import (
    TargetTimeIn, ActualTimeIn, RegisterActivities
)
from app.models.common_model import CheckDate
from db import db_model
from db.database import get_db
from lib.security import get_current_user
from lib.log_conf import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, IntegrityError
from pydantic import ValidationError

router = APIRouter()


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
        fetch_activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == current_user["username"]).one_or_none()
        if fetch_activity is None:
            raise HTTPException(status_code=404, detail=f"{date}の情報は未登録です")

        target_time = fetch_activity.target_time
        actual_time = fetch_activity.actual_time
        is_achieved = fetch_activity.is_achieved

        if is_achieved:
            bonus = fetch_activity.bonus
            penalty = 0
        else:
            fetch_income = db.query(db_model.Income).filter(
                db_model.Income.year_month == f"{year}-{month}",
                db_model.Income.username == current_user["username"]).one_or_none()
            if fetch_income is None:
                raise HTTPException(status_code=404, detail=f"{year}-{month}の月収が未登録です")

            bonus = round(((fetch_income.salary / 200) * actual_time), 2)
            penalty = round(((fetch_income.salary / 200) * max((target_time - actual_time), 0)), 2)

        logger.info(f"{current_user['username']}が{date}の活動実績を取得")
        return {"date": date,
                "target_time": target_time,
                "actual_time": actual_time,
                "is_achieved": is_achieved,
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


@ router.post("/activities/{year}/{month}/{day}/target",
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

        insert_data = db_model.Activity(
            date=date, target_time=target_time, username=username)
        db.add(insert_data)
        db.commit()
        message = f"{date}の目標時間を{target_time}時間に設定しました"
        logger.info(f"{current_user['username']}が{date}の目標時間を登録")
        return {"date": date,
                "target_time": target_time,
                "actual_time": 0,
                "is_achieved": False,
                "message": message}
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


@ router.put("/activities/{year}/{month}/{day}/actual",
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

        fetch_activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == current_user["username"]).one_or_none()
        if not fetch_activity:
            raise HTTPException(status_code=404, detail=f"先に{date}の目標を入力して下さい")
        if fetch_activity.bonus == 0 and fetch_activity.penalty == 0:
            fetch_activity.actual_time = actual_time
            db.commit()
            logger.info(f"{current_user['username']}が{date}の活動時間を登録")
            return {"date": date,
                    "target_time": fetch_activity.target_time,
                    "actual_time": actual_time,
                    "is_achieved": False,
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


@ router.put("/activities/{year}/{month}/{day}/finish",
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

        fetch_activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == current_user["username"]).one_or_none()
        if not fetch_activity:
            raise HTTPException(status_code=404, detail=f"{date}の活動実績は登録されていません")

        target_time = fetch_activity.target_time
        actual_time = fetch_activity.actual_time
        year_month = f"{year}-{month}"

        if fetch_activity.is_achieved or (fetch_activity.bonus != 0 or fetch_activity.penalty != 0):
            raise HTTPException(status_code=400, detail=f"{date}の実績は登録済みです")
        fetch_income = db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month,
            db_model.Income.username == current_user["username"]).one_or_none()
        if not fetch_income:
            raise HTTPException(status_code=404, detail=f"{year_month}の月収が未登録です")

        # 達成している場合はincomesテーブルのボーナスを、達成していない場合はpenaltyを加算する。
        if actual_time >= target_time:
            fetch_activity.is_achieved = True
            bonus = round(((fetch_income.salary / 200) * actual_time), 2)
            fetch_activity.bonus = bonus
            fetch_income.total_bonus += bonus
            message = f"目標達成！{bonus}万円({int(bonus * 10000)}円)ボーナス追加！"
        else:
            fetch_activity.is_achieved = False
            diff = round((target_time - actual_time), 1)
            penalty = round(((fetch_income.salary / 200) * diff), 2)
            fetch_activity.penalty = penalty
            fetch_income.total_penalty += penalty
            message = f"{diff}時間足りませんでした。{penalty}万円({int(penalty * 10000)}円)ペナルティ追加"
        db.commit()
        logger.info(f"{current_user['username']}が{date}の活動を終了")
        return {
            "date": date,
            "target_time": target_time,
            "actual_time": actual_time,
            "is_achieved": fetch_activity.is_achieved,
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


@ router.get("/activities/{year}/{month}", status_code=200)
def get_month_activities(year: int,
                         month: int,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """ 特定月のデータを取得 """
    try:
        CheckDate(year=year, month=month)
        year_month = f"{year}-{month}"
        # 検索範囲の指定
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)

        activities = db.query(db_model.Activity).filter(
            db_model.Activity.date.between(start_date, end_date),
            db_model.Activity.username == current_user["username"]).order_by(
                db_model.Activity.date).all()
        if not activities:
            raise HTTPException(status_code=404,
                                detail=f"{year_month}内の活動は登録されていません")
        fetch_income = db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month,
            db_model.Income.username == current_user["username"]).one()
        total_monthly_income = fetch_income.salary + fetch_income.total_bonus
        success_days = [act for act in activities if act.is_achieved is True]
        logger.info(f"{current_user['username']}が{year_month}の活動実績を取得")
        return {"total_monthly_income": total_monthly_income,
                "salary": fetch_income.salary,
                "pay_adjustment": round((fetch_income.total_bonus - fetch_income.total_penalty), 2),
                "bonus": fetch_income.total_bonus,
                "penalty": fetch_income.total_penalty,
                "success_days": len(success_days),
                "fail_days": len(activities) - len(success_days),
                "activity_list": activities}
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{year_month}の給料は登録されていません")
    except ValidationError as validate_e:
        raise HTTPException(status_code=422, detail=str(validate_e.errors()[0]["ctx"]["error"]))
    except Exception:
        logger.error(f"月別の活動実績の取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@ router.get("/activities/total/", status_code=200)
def get_total_activity_result(db: Session = Depends(get_db),
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
        fetch_incomes = db.query(db_model.Income).filter(
            db_model.Income.username == current_user["username"]).all()
        if not fetch_incomes:
            raise HTTPException(status_code=404,
                                detail=f"{current_user['username']}の給料は登録されていません")
        total_salary = sum([income.salary for income in fetch_incomes])
        total_bonus = round(sum([income.total_bonus for income in fetch_incomes]), 2)
        total_penalty = round(sum([income.total_penalty for income in fetch_incomes]), 2)
        total_income = total_salary + total_bonus - total_penalty
        success_days = [act for act in activities if act.is_achieved is True]
        logger.info(f"{current_user['username']}が全期間の活動実績を取得")
        return {"total_income": total_income,
                "total_salary": total_salary,
                "pay_adjustment": round(total_bonus - total_penalty, 2),
                "total_bonus": round(total_bonus, 2),
                "total_penalty": round(total_penalty, 2),
                "success_days": len(success_days),
                "fail_days": len(activities) - len(success_days)}
    except HTTPException as http_e:
        raise http_e
    except Exception:
        logger.error(f"月別の活動実績の取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
