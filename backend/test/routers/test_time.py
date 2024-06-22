# 事前処理

def register_target(client):
    data = {"date": "2024-05-05", "target_time": 5}
    client.post("/target", json=data)


def register_actual(client):
    data = {"actual_time": 5, "date": "2024-05-05"}
    client.put("/actual", json=data)


def finish_activity(client):
    data = {"date": "2024-05-05"}
    client.put("/finish", json=data)


def register_monthly_income(client):
    data = {"monthly_income": 23, "year_month": "2024-05"}
    client.post("/income", json=data)

# 事前処理ここまで


# 以降テスト関数

def test_register_target_success(client):
    data = {"date": "2024-05-05", "target_time": 5}
    response = client.post("/target", json=data)
    assert response.status_code == 201


def test_register_target_incorrect_date_format_slash(client):
    """ 日付の形式が-ではなく/の場合 """
    data = {"date": "2024/05/05", "target_time": 5}
    response = client.post("/target", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "入力形式が違います。正しい形式:YYYY-MM-DD"}


def test_register_target_incorrect_date_format_missing_zero(client):
    """ 日付の書き方が不正(一桁の場合は0xの形式が正しい)の場合 """
    data = {"date": "2024-5-5", "target_time": 5}
    response = client.post("/target", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "入力形式が違います。正しい形式:YYYY-MM-DD"}


def test_register_actual_success(client):
    register_target(client)
    data = {"actual_time": 5, "date": "2024-05-05"}
    response = client.put("/actual", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "date": data['date'],
        "target_time": 5,
        "actual_time": data["actual_time"],
        "message": f"活動時間を{data['actual_time']}時間に設定しました。"
    }


def test_register_actual_before_register_target(client):
    """ 目標時間登録前に活動時間を登録した場合 """
    data = {"actual_time": 5, "date": "2024-05-06"}
    response = client.put("/actual", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": f"先に{data['date']}の目標を入力して下さい"}


def test_register_actual_after_finish(client):
    """ 活動を終了した日の活動時間を更新しようとした場合 """
    register_target(client)
    register_actual(client)
    register_monthly_income(client)
    finish_activity(client)
    data = {"actual_time": 5, "date": "2024-05-05"}
    response = client.put("/actual", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail":
                               f"{data['date']}の活動実績は既に確定済みです。変更できません"}


def test_finish_activity_success(client):
    register_target(client)
    register_actual(client)
    register_monthly_income(client)
    data = {"date": "2024-05-05"}
    response = client.put("/finish", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "date": data["date"],
        "target_time": 5.0,
        "actual_time": 5.0,
        "is_achieved": True,
        "message": "目標達成！ボーナス追加！"}


def test_finish_activity_before_register_actual(client):
    """ 活動時間登録前に活動を終了しようとした場合 """
    register_target(client)
    data = {"date": "2024-05-05"}
    response = client.put("/finish", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": f"{data['date']}の活動時間を登録して下さい"}


def test_finish_activity_without_register_income(client):
    """ 月収を登録せずに活動を終了しようとした場合 """
    register_target(client)
    register_actual(client)
    data = {"date": "2024-05-05"}
    response = client.put("/finish", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "2024-05の月収が未登録です"}


def test_get_today_situation(client):
    """ 活動終了記録まで行った日の情報を取得 """
    register_target(client)
    register_actual(client)
    register_monthly_income(client)
    finish_activity(client)
    date = "2024-05-05"
    response = client.get(f"/situation/{date}")
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "is_achieved": True,
                               "bonus": 0.1}


def test_get_today_situation_without_register_activity(client):
    """ 活動記録が未登録の日の情報を取得する場合 """
    date = "2024-05-10"
    response = client.get(f"/situation/{date}")
    assert response.status_code == 400
    assert response.json() == {"detail": f"{date}の情報は登録されていません"}
