# api/jobs.py
import os
from datetime import datetime, timedelta
from typing import Any
import redis
from rq import Queue
from rq_scheduler import Scheduler
from api.metrics import REQUEST_COUNT

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = redis.from_url(REDIS_URL)
queue_default = Queue("default", connection=redis_conn)
scheduler = Scheduler(queue=queue_default, connection=redis_conn)

def send_email(template: str, to: str, payload: dict[str, Any]) -> None:
    """Simulate email sending."""
    print(f"Sending email: {template} to {to} with {payload}")
    REQUEST_COUNT.labels(method="email", endpoint="send", status="sent").inc()

# Example scheduled job
def schedule_test_job():
    when = datetime.utcnow() + timedelta(seconds=30)
    scheduler.enqueue_at(when, send_email, "welcome", "user@example.com", {"name": "Test User"})
    print(f"Scheduled job for {when}")

if __name__ == "__main__":
    schedule_test_job()
    scheduler.run()