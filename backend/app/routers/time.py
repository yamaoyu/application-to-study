import traceback
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from app.models.time_model import (
    TargetTimeIn, ActualTimeIn, RegisterActivities
)
from db import db_model
from db.database import get_db
from lib.security import get_current_user
from lib.log_conf import logger
from lib.check_data import set_date_format, is_valid_input_time
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, IntegrityError

router = APIRouter()


@router.get("/activities/{year}/{month}/{day}", status_code=200)
def day_activities(year: str,
                   month: str,
                   day: str,
                   db: Session = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    """ 特定日の活動実績を確認する """
    try:
        date = set_date_format(year, month, day)
        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == current_user["username"]).one()

        target_time = activity.target_time
        actual_time = activity.actual_time
        is_achieved = activity.is_achieved
        bonus = 0.1 if is_achieved else 0.0
        logger.info(f"{current_user['username']}が{date}の活動実績を取得")
        return {"date": date,
                "target_time": target_time,
                "actual_time": actual_time,
                "is_achieved": is_achieved,
                "bonus": bonus}
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"{date}の情報は未登録です")
    except Exception:
        logger.error(f"日別の活動実績の取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.post("/activities/{year}/{month}/{day}/target",
             status_code=201,
             response_model=RegisterActivities)
def register_target_time(target: TargetTimeIn,
                         year: str,
                         month: str,
                         day: str,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """ 目標活動時間を登録、登録済みなら更新する """
    try:
        username = current_user["username"]
        target_time = target.target_time
        date = set_date_format(year, month, day)
        if not is_valid_input_time(target_time):
            raise HTTPException(status_code=400,
                                detail="入力時間は0.5~12.5の範囲で入力してください")

        insert_data = db_model.Activity(
            date=date, target_time=target_time, username=username)
        db.add(insert_data)
        db.commit()
        db.refresh(insert_data)
        message = f"{date}の目標時間を{target_time}時間に設定しました"
        logger.info(f"{current_user['username']}が{date}の目標時間を登録")
        return {"date": date,
                "target_time": target_time,
                "actual_time": 0,
                "is_achieved": False,
                "message": message}
    except HTTPException as http_e:
        raise http_e
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail=f"{date}の目標時間は既に登録済みです")
    except Exception:
        logger.error(f"目標時間の登録に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.put("/activities/{year}/{month}/{day}/actual",
            status_code=200,
            response_model=RegisterActivities)
def update_actual_time(actual: ActualTimeIn,
                       year: str,
                       month: str,
                       day: str,
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    """ 目標時間が登録済みの場合、活動時間を入力 """
    try:
        actual_time = actual.actual_time
        date = set_date_format(year, month, day)
        if not is_valid_input_time(actual_time):
            raise HTTPException(status_code=400,
                                detail="入力時間は0.5~12.5の範囲で入力してください")

        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == current_user["username"]).one()
        if activity.is_achieved is not True:
            activity.actual_time = actual_time
            db.commit()
            logger.info(f"{current_user['username']}が{date}の活動時間を登録")
            return {"date": date,
                    "target_time": activity.target_time,
                    "actual_time": actual_time,
                    "is_achieved": False,
                    "message": f"活動時間を{actual_time}時間に設定しました"}
        else:
            raise HTTPException(status_code=400,
                                detail=f"{date}の活動実績は既に確定済みです。変更できません")
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"先に{date}の目標を入力して下さい")
    except Exception:
        logger.error(f"活動時間の登録に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500,
                            detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.put("/activities/{year}/{month}/{day}/finish",
            status_code=200,
            response_model=RegisterActivities)
def finish_activities(year: str,
                      month: str,
                      day: str,
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    """ 特定日の作業時間を確定し、目標を達成しているのかを確認する """
    try:
        date = set_date_format(year, month, day)

        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == current_user["username"]).one()
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"{date}の情報は登録されていません")
    except Exception:
        logger.error(f"活動終了処理に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")

    try:
        target_time = activity.target_time
        actual_time = activity.actual_time
        year_month = f"{year}-{month}"

        if activity.is_achieved is True:
            raise HTTPException(status_code=400, detail=f"{date}の実績は登録済みです")
        # 達成している場合はIncomeテーブルのボーナスを加算する。
        if actual_time >= target_time:
            salary = db.query(db_model.Income).filter(
                db_model.Income.year_month == year_month,
                db_model.Income.username == current_user["username"]).one()
            activity.is_achieved = True
            message = "目標達成！ボーナス追加！"
            salary.bonus = float(salary.bonus) + 0.1
        # 達成していない場合はIncomeテーブルを更新しない
        else:
            activity.is_achieved = False
            diff = round((target_time - actual_time), 1)
            message = f"{diff}時間足りませんでした"
        db.commit()
        logger.info(f"{current_user['username']}が{date}の活動を終了")
        return {
            "date": date,
            "target_time": target_time,
            "actual_time": actual_time,
            "is_achieved": activity.is_achieved,
            "message": message}
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{year_month}の月収が未登録です")
    except Exception:
        logger.error(f"活動終了処理に失敗しました\n{traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")


@router.get("/activities/{year}/{month}", status_code=200)
def month_activities(year: str,
                     month: str,
                     db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    """ 特定月のデータを取得 """
    try:
        year_month = set_date_format(year, month)
        # 検索範囲の指定
        start_date = datetime(int(year), int(month), 1).date()
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1).date()
        else:
            end_date = datetime(int(year), int(month) + 1, 1).date()

        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date.between(start_date, end_date),
            db_model.Activity.username == current_user["username"]).order_by(
                db_model.Activity.date).all()
        if not activity:
            raise HTTPException(status_code=404,
                                detail=f"{year_month}内の活動は登録されていません")
        salary = db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month,
            db_model.Income.username == current_user["username"]).one()
        total_monthly_income = salary.monthly_income + salary.bonus
        success_days = [act for act in activity if act.is_achieved is True]
        logger.info(f"{current_user['username']}が{year_month}の活動実績を取得")
        return {"total_monthly_income": total_monthly_income,
                "base_income": salary.monthly_income,
                "total_bonus": salary.bonus,
                "success_days": len(success_days),
                "activity_lists": activity}
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=404,
                            detail=f"{year_month}の給料は登録されていません")
    except Exception:
        logger.error(f"月別の活動実績の取得に失敗しました\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="サーバーでエラーが発生しました。管理者にお問い合わせください")
