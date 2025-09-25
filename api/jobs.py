import os
from datetime import datetime, timedelta, timezone
from typing import Any

import redis
from rq import Queue
from rq_scheduler import Scheduler

from prometheus_client import Counter
from metrics import JOBS_SENT, MAIL_SENT

# ===== RQ/Redis =====
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = redis.from_url(REDIS_URL)

queue_default = Queue("default", connection=redis_conn)
scheduler = Scheduler(queue=queue_default, connection=redis_conn)


# ===== Псевдо-отправка писем (заготовка под SMTP) =====
def send_email(template: str, to: str, payload: dict[str, Any]) -> None:
    """
    Здесь подключите реальный SMTP позже.
    Пока просто считаем метрики и пишем в stdout (видно в логах воркера).
    """
    # Имитация отправки
    print(f"[MAIL] template={template} to={to} payload={payload}")
    MAIL_SENT.labels(template=template, status="queued").inc()


# ===== Бизнес-джобы =====
def job_lesson_reminder(student_email: str, lesson_id: int, start_at: str) -> None:
    """
    Напоминание «урок завтра».
    """
    send_email(
        template="lesson_reminder",
        to=student_email,
        payload={"lesson_id": lesson_id, "start_at": start_at},
    )


def job_weekly_digest(parent_email: str, student_name: str, period: str, stats: dict) -> None:
    """
    Недельный дайджест родителям.
    stats: {"lessons": int, "assignments_done": int, "assignments_total": int, "level": int}
    """
    send_email(
        template="weekly_digest",
        to=parent_email,
        payload={"student": student_name, "period": period, "stats": stats},
    )


def job_invoice_due_reminder(payer_email: str, invoice_id: int, amount: float, due_date: str) -> None:
    """
    Напоминание «оплата через 3 дня».
    """
    send_email(
        template="invoice_due",
        to=payer_email,
        payload={"invoice_id": invoice_id, "amount": amount, "due_date": due_date},
    )


# ===== Хелперы постановки задач =====
def enqueue_lesson_reminder(student_email: str, lesson_id: int, start_at: datetime) -> None:
    run_at = start_at - timedelta(days=1)
    if run_at.tzinfo is None:
        run_at = run_at.replace(tzinfo=timezone.utc)
    scheduler.enqueue_at(
        run_at, job_lesson_reminder, student_email=student_email, lesson_id=lesson_id, start_at=start_at.isoformat()
    )
    JOBS_SENT.labels(kind="lesson_reminder").inc()


def enqueue_weekly_digest(parent_email: str, student_name: str, week_monday: datetime, stats: dict) -> None:
    period = f"{week_monday.date()}..{(week_monday + timedelta(days=6)).date()}"
    # шедулим на воскресенье 18:00 локального времени (условно UTC)
    run_at = (week_monday + timedelta(days=6)).replace(hour=18, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    scheduler.enqueue_at(
        run_at, job_weekly_digest, parent_email=parent_email, student_name=student_name, period=period, stats=stats
    )
    JOBS_SENT.labels(kind="weekly_digest").inc()


def enqueue_invoice_due(payer_email: str, invoice_id: int, amount: float, due_date: datetime) -> None:
    run_at = (due_date - timedelta(days=3)).replace(tzinfo=timezone.utc)
    scheduler.enqueue_at(
        run_at,
        job_invoice_due_reminder,
        payer_email=payer_email,
        invoice_id=invoice_id,
        amount=float(amount),
        due_date=due_date.date().isoformat(),
    )
    JOBS_SENT.labels(kind="invoice_due").inc()


# ===== Периодические задачи (пример) =====
def schedule_recurring_jobs() -> None:
    """
    Регистрирует периодические джобы (idempotent).
    Пример: health-пинг раз в минуту, чтобы видеть работу scheduler.
    """
    job_id = "heartbeat-minute"
    # удалим существующую с тем же id
    for j in scheduler.get_jobs():
        if j.id == job_id:
            scheduler.cancel(j)
    scheduler.cron(
        "*/1 * * * *",  # каждую минуту
        func=send_email,
        kwargs={"template": "heartbeat", "to": "ops@local", "payload": {"ok": True}},
        id=job_id,
        repeat=None,
        queue_name="default",
    )
    JOBS_SENT.labels(kind="heartbeat").inc()


if __name__ == "__main__":
    # Позволяет вручную прогреть периодические задачи:
    schedule_recurring_jobs()
    print("Scheduled recurring jobs.")
