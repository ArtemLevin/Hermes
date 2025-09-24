import os, requests

BASE = os.getenv("BASE", "http://localhost:8000")

def test_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200

def test_auth_and_students():
    # Регистрируем пользователя (идемпотентно)
    requests.post(
        f"{BASE}/auth/register",
        json={"email": "tutor@example.com", "password": "tutor", "role": "tutor"},
    )
    # Логинимся
    r = requests.post(
        f"{BASE}/auth/login",
        json={"email": "tutor@example.com", "password": "tutor"},
    )
    assert r.status_code == 200
    token = r.json()["token"]

    # Получаем список учеников
    r = requests.get(f"{BASE}/students", headers={"Authorization": f"Bearer {token}"})
    # Пока эндпоинт не проверяет токен, допускаем 200 без auth
    assert r.status_code == 200
