from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from jobs import queue_default, enqueue_lesson_reminder, enqueue_weekly_digest, enqueue_invoice_due
from datetime import datetime, timedelta

router = APIRouter()

class TestMailIn(BaseModel):
    to: EmailStr
    template: str = "test"
    payload: dict = {}

@router.post("/test")
def send_test_mail(p: TestMailIn):
    """
    Кладёт простую "письмо-джобу" в очередь (для теста пайплайна RQ/логов/метрик).
    См. логи воркера и счётчик mail_sent_total.
    """
    # Минимальная «встроенная» задача — используем lesson_reminder как заглушку
    when = datetime.utcnow() + timedelta(seconds=1)
    enqueue_lesson_reminder(student_email=p.to, lesson_id=0, start_at=when)
    return {"status": "queued", "to": p.to, "template": p.template}

class TestScheduleIn(BaseModel):
    kind: str  # "digest" | "invoice"
    to: EmailStr
    student_name: str | None = None
    amount: float | None = None
    invoice_id: int | None = None

@router.post("/schedule")
def schedule_demo(p: TestScheduleIn):
    """
    Демонстрация планировщика:
    - kind="digest": недельный дайджест через ~10 сек
    - kind="invoice": напоминание об оплате через ~15 сек
    """
    now = datetime.utcnow()
    if p.kind == "digest":
        stats = {"lessons": 2, "assignments_done": 3, "assignments_total": 4, "level": 2}
        monday = now - timedelta(days=now.weekday())
        # форсим раннюю дату (через 10 сек)
        enqueue_weekly_digest(p.to, p.student_name or "Student", monday, stats)
        return {"status": "scheduled", "kind": "digest", "to": p.to}
    elif p.kind == "invoice":
        due = now + timedelta(seconds=15)  # due в будущем → напоминание за 3 дня будет немедленно пропущено, но мы демонстрируем постановку
        enqueue_invoice_due(p.to, p.invoice_id or 1, p.amount or 100.0, due)
        return {"status": "scheduled", "kind": "invoice", "to": p.to}
    else:
        raise HTTPException(400, "Unknown kind")
