from conftest import test_username
# 事前処理


def setup_target_for_test(client, login_and_get_token):
    data = {"date": "2024-05-05", "target_time": 5}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    client.post("/target", json=data, headers=headers)


def setup_actual_for_test(client, login_and_get_token):
    data = {"actual_time": 5, "date": "2024-05-05"}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    client.put("/actual", json=data, headers=headers)


def setup_finish_activity_for_test(client, login_and_get_token):
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"date": "2024-05-05"}
    client.put("/finish", json=data, headers=headers)


def setup_monthly_income_for_test(client, login_and_get_token):
    data = {"monthly_income": 23, "year_month": "2024-05"}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    client.post("/income", json=data, headers=headers)

# 事前処理ここまで


# 以降テスト関数

def test_register_target_success(client, login_and_get_token):
    data = {"date": "2024-05-05", "target_time": 5}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/target", json=data, headers=headers)
    assert response.status_code == 201


def test_register_target_without_slash(client,
                                       login_and_get_token):
    """ 日付の形式が-ではなく/の場合 """
    data = {"date": "2024/05/05", "target_time": 5}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/target", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "入力形式が違います。正しい形式:YYYY-MM-DD"}


def test_register_target_missing_zero(client,
                                      login_and_get_token):
    """ 日付の書き方が不正(一桁の場合は0xの形式が正しい)の場合 """
    data = {"date": "2024-5-5", "target_time": 5}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/target", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "入力形式が違います。正しい形式:YYYY-MM-DD"}


def test_register_actual_success(client, login_and_get_token):
    setup_target_for_test(client, login_and_get_token)
    data = {"actual_time": 5, "date": "2024-05-05"}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/actual", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "date": data['date'],
        "target_time": 5,
        "actual_time": data["actual_time"],
        "message": f"活動時間を{data['actual_time']}時間に設定しました。"
    }


def test_register_actual_before_register_target(client, login_and_get_token):
    """ 目標時間登録前に活動時間を登録した場合 """
    data = {"actual_time": 5, "date": "2024-05-06"}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/actual", json=data, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": f"先に{data['date']}の目標を入力して下さい"}


def test_register_actual_after_finish(client, login_and_get_token):
    """ 活動を終了した日の活動時間を更新しようとした場合 """
    setup_target_for_test(client, login_and_get_token)
    setup_actual_for_test(client, login_and_get_token)
    setup_monthly_income_for_test(client, login_and_get_token)
    setup_finish_activity_for_test(client, login_and_get_token)
    data = {"actual_time": 5, "date": "2024-05-05"}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/actual", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail":
                               f"{data['date']}の活動実績は既に確定済みです。変更できません"}


def test_finish_activity_success(client, login_and_get_token):
    setup_target_for_test(client, login_and_get_token)
    setup_actual_for_test(client, login_and_get_token)
    setup_monthly_income_for_test(client, login_and_get_token)
    data = {"date": "2024-05-05"}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/finish", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "date": data["date"],
        "target_time": 5.0,
        "actual_time": 5.0,
        "is_achieved": True,
        "message": "目標達成！ボーナス追加！"}


def test_finish_activity_before_register_actual(client, login_and_get_token):
    """ 活動時間登録前に活動を終了しようとした場合 """
    setup_target_for_test(client, login_and_get_token)
    data = {"date": "2024-05-05"}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/finish", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": f"{data['date']}の活動時間を登録して下さい"}


def test_finish_activity_without_register_income(client, login_and_get_token):
    """ 月収を登録せずに活動を終了しようとした場合 """
    setup_target_for_test(client, login_and_get_token)
    setup_actual_for_test(client, login_and_get_token)
    data = {"date": "2024-05-05"}
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/finish", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "2024-05の月収が未登録です"}


def test_get_today_situation(client, login_and_get_token):
    """ 活動終了記録まで行った日の情報を取得 """
    setup_target_for_test(client, login_and_get_token)
    setup_actual_for_test(client, login_and_get_token)
    setup_monthly_income_for_test(client, login_and_get_token)
    setup_finish_activity_for_test(client, login_and_get_token)
    date = "2024-05-05"
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/situation/{date}", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"date": date,
                               "target_time": 5.0,
                               "actual_time": 5.0,
                               "is_achieved": True,
                               "bonus": 0.1,
                               "username": test_username}


def test_get_today_situation_before_register_activity(client,
                                                      login_and_get_token):
    """ 活動記録が未登録の日の情報を取得する場合 """
    date = "2024-05-10"
    access_token = login_and_get_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/situation/{date}", headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": f"{date}の情報は登録されていません"}
