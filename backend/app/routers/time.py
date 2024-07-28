import re
from logging import getLogger, basicConfig, INFO
from fastapi import APIRouter, HTTPException, Depends
from app.models.time_model import (
    ResponseTargetTime, TargetTimeIn,
    ActualTimeIn, ResponseStudyTime, DateIn
)
from db import db_model
from db.database import get_db
from security import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

router = APIRouter()

basicConfig(level=INFO, format="%(levelname)s: %(message)s")
logger = getLogger(__name__)

date_pattern = r"^\d{4}-\d{2}-\d{2}$"
year_month_pattern = r"^\d{4}-\d{2}$"


@router.get("/situation/{date}", status_code=200)
def show_today_situation(date: str,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """ その日の活動時間を確認する """
    # dateのフォーマットがYYYY-MM-DDか確認
    if not re.match(date_pattern, date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    try:
        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == current_user["username"]).one()

        target_time = activity.target
        if not target_time:
            return {"date": date, "target_time": "未設定", "actual_time": "未設定"}

        actual_time = activity.actual
        if not actual_time:
            return {"date": date,
                    "target_time": target_time,
                    "actual_time": "未設定"}

        is_achieved = activity.is_achieved
        if is_achieved is None:
            return {"date": date, "target_time": target_time,
                    "actual_time": actual_time, "is_achieved": "未完了"}

        bonus = lambda is_achieved: 0.1 if is_achieved else 0  # noqa
        logger.info(f"{current_user['username']}が{date}の活動実績を取得")
        return {"date": date,
                "target_time": target_time,
                "actual_time": actual_time,
                "is_achieved": is_achieved,
                "bonus": bonus(is_achieved),
                "username": current_user["username"]}
    except NoResultFound:
        raise HTTPException(status_code=400, detail=f"{date}の情報は登録されていません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.post("/target",
             status_code=201,
             response_model=ResponseTargetTime)
def register_today_target(target: TargetTimeIn,
                          db: Session = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    """ 目標活動時間を登録、登録済みなら更新する """
    username = current_user["username"]
    target_time = target.target_time
    date = target.date
    # dateのフォーマットがYYYY-MM-DDか確認
    if not re.match(date_pattern, date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    data = db_model.Activity(date=date, target=target_time, username=username)
    try:
        db.add(data)
        db.commit()
        db.refresh(data)
        message = f"{date}の目標時間を{target_time}時間に設定しました"
        logger.info(f"{current_user['username']}が{date}の目標時間を登録")
        return {"target_time": target_time, "date": date, "message": message}
    except HTTPException as http_e:
        raise http_e
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"{data.date}の目標時間は既に登録済みです")


@router.put("/actual",
            status_code=200,
            response_model=ResponseStudyTime)
def register_actual_time(actual: ActualTimeIn,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """ 目標時間が登録済みの場合、活動時間を入力 """
    actual_time = actual.actual_time
    date = actual.date
    # dateのフォーマットがYYYY-MM-DDか確認
    if not re.match(date_pattern, date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    try:
        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == current_user["username"]).one()
        if activity.is_achieved is None:
            activity.actual = actual_time
            db.commit()
            logger.info(f"{current_user['username']}が{date}の活動時間を登録")
            return {"date": date,
                    "actual_time": actual_time,
                    "target_time": activity.target,
                    "message": f"活動時間を{actual_time}時間に設定しました。",
                    "username": current_user['username']}
        else:
            raise HTTPException(status_code=400,
                                detail=f"{date}の活動実績は既に確定済みです。変更できません")
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"先に{date}の目標を入力して下さい")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=str(e))


@router.put("/finish", status_code=200)
def finish_today_work(date: DateIn,
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    """ その日の作業時間を確定し、目標を達成しているのかを確認する """
    date = date.date
    # dateのフォーマットがYYYY-MM-DDか確認
    if not re.match(date_pattern, date):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM-DD")
    try:
        activity = db.query(db_model.Activity).filter(
            db_model.Activity.date == date,
            db_model.Activity.username == current_user["username"]).one()
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=400, detail=f"{date}の情報は登録されていません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    try:
        target_time = activity.target
        actual_time = activity.actual
        year_month = date[:7]

        if actual_time is None:
            raise HTTPException(status_code=400, detail=f"{date}の活動時間を登録して下さい")
        elif activity.is_achieved is not None:
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
        raise HTTPException(status_code=400,
                            detail=f"{year_month}の月収が未登録です")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=e)


@router.get("/month")
def get_month_situation(date: DateIn,
                        db: Session = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    """ 月毎のデータを取得 """
    year_month = date.date
    # dateのフォーマットがYYYY-MMか確認
    if not re.match(year_month_pattern, year_month):
        raise HTTPException(status_code=400,
                            detail="入力形式が違います。正しい形式:YYYY-MM")
    activity = db.query(db_model.Activity).filter(
        db_model.Activity.date.like(f"{year_month}%"),
        db_model.Activity.username == current_user["username"]).all()
    if not activity:
        raise HTTPException(status_code=400,
                            detail=f"{year_month}内の活動は登録されていません")
    try:
        salary = db.query(db_model.Income).filter(
            db_model.Income.year_month == year_month,
            db_model.Income.username == current_user["username"]).one()
        total_monthly_income = salary.monthly_income + salary.bonus
        success_days = [act for act in activity if act.is_achieved is True]
        logger.info(f"{current_user['username']}が{year_month}の活動実績を取得")
        return {"total_monthly_income": total_monthly_income,
                "base income": salary.monthly_income,
                "total bonus": salary.bonus,
                "success days": len(success_days),
                "activity lists": activity}
    except HTTPException as http_e:
        raise http_e
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail=f"{year_month}の給料は登録されていません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
