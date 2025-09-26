import os
import requests
from datetime import datetime, timedelta

BASE = os.getenv("BASE", "http://localhost:8000")

def test_assignments_crud():
    # создаём ДЗ на первого попавшегося студента (id=1)
    r = requests.post(f"{BASE}/assignments", json={
        "student_id": 1,
        "title": "Проверочное ДЗ",
        "reward_type": "coin",
        "due_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "topic_ids": []
    })
    assert r.status_code == 200
    aid = r.json()["id"]

    # старт ДЗ
    r = requests.post(f"{BASE}/assignments/{aid}/start")
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"

    # сабмит ДЗ
    r = requests.post(f"{BASE}/assignments/{aid}/submit", json={"artifacts": [], "grade": 5})
    assert r.status_code == 200
    assert r.json()["status"] == "done"
    assert "gained_points" in r.json()

    # листинг
    r = requests.get(f"{BASE}/assignments?student_id=1")
    assert r.status_code == 200
    assert "items" in r.json()

def test_analytics_and_radar():
    r = requests.get(f"{BASE}/analytics/exam-forecast", params={"student_id": 1})
    assert r.status_code == 200
    assert "predicted_score" in r.json()

    r = requests.get(f"{BASE}/analytics/priority-radar")
    assert r.status_code == 200
    assert "items" in r.json()

def test_mems_and_tournaments():
    # мем
    r = requests.post(f"{BASE}/mems", json={"url": "https://i.imgflip.com/1bij.jpg", "caption": "go!", "student_id": 1})
    assert r.status_code == 200
    mid = r.json()["id"]

    r = requests.get(f"{BASE}/mems?student_id=1")
    assert r.status_code == 200
    assert r.json()["total"] >= 1

    # турнир
    r = requests.post(f"{BASE}/tournaments", json={"name": "Тест Турнир"})
    assert r.status_code == 200
    tid = r.json()["id"]

    r = requests.post(f"{BASE}/tournaments/{tid}/join", json={"student_id": 1})
    assert r.status_code == 200

    r = requests.post(f"{BASE}/tournaments/{tid}/score", json={"student_id": 1, "points": 3})
    assert r.status_code == 200
    assert r.json()["points"] >= 3

    r = requests.get(f"{BASE}/tournaments/{tid}/leaderboard")
    assert r.status_code == 200
    assert "leaderboard" in r.json()
