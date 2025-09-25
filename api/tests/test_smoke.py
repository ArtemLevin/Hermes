import os
import time
import requests

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
    assert r.status_code == 200

def test_metrics_and_notifications():
    # Доступность /metrics
    r = requests.get(f"{BASE}/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text

    # Тестовая постановка письма в очередь
    r = requests.post(
        f"{BASE}/notifications/test",
        json={"to": "test@example.com", "template": "test", "payload": {"x": 1}},
    )
    assert r.status_code == 200
    assert r.json().get("status") == "queued"

    # Дать воркеру время обработать (если поднят worker)
    time.sleep(2)

    # Повторная проверка метрик — должен расти счётчик запросов
    r2 = requests.get(f"{BASE}/metrics")
    assert r2.status_code == 200
    assert "mail_sent_total" in r2.text  # метрика из jobs.send_email
