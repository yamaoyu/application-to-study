import re
from fastapi import HTTPException
from datetime import datetime


def set_date_format(year, month, day=None):
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


def is_valid_input_time(time):
    time_str = str(time)
    if re.match(r"^((1[0-2]|\d)\.[0|5])$", time_str):
        return True
    return False
