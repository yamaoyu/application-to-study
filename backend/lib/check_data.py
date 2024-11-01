import re
from fastapi import HTTPException
from datetime import datetime


def set_date_format(year, month, day=None):
    """ 入力された日付が正しいのか確認する """
    year_format = r"^20\d{2}$"
    month_format = r"^(?:[1-9]|1[0-2])$"
    day_format = r"^(?:[1-9]|[1-2][0-9]|[3][0-1])$"
    if not re.match(year_format, year):
        raise HTTPException(status_code=400, detail="年は20xxの形式で入力してください")
    if not re.match(month_format, month):
        raise HTTPException(status_code=400,
                            detail="月は1~12で入力してください。一桁の場合01とせず1のみを入力してください")
    # dayが引数で渡されていない場合はスキップする
    if day:
        if not re.match(day_format, day):
            raise HTTPException(status_code=400, detail="日は1~31で入力してください")
        try:
            date = year + "-" + month + "-" + day
            datetime.strptime(date, "%Y-%m-%d")
        except Exception:
            raise HTTPException(status_code=400, detail="日付が不正です")
    else:
        date = year + "-" + month
    return date


def check_user_login_data(username, plain_password, email):
    """ ユーザー作成時のデータの整合性を確認 """
    if not (3 <= len(username) <= 16):
        raise HTTPException(status_code=400,
                            detail="ユーザー名は3文字以上、16文字以下としてください")
    if not (6 <= len(plain_password) <= 12):
        raise HTTPException(status_code=400,
                            detail="パスワードは6文字以上、16文字以下としてください")
    if email is not None and "@" not in email:
        raise HTTPException(status_code=400,
                            detail="正しいメールアドレスを入力してください")
