import logging
from functools import wraps
from typing import Any, Callable, Optional

from logging_config import get_request_id

log = logging.getLogger("api.audit")

def audit_event(action: str, **fields: Any) -> None:
    """
    Пишет структурированное событие аудита в JSON-лог.
    Пример: audit_event("created_lesson", user_id=1, lesson_id=42)
    """
    payload = {"action": action, "request_id": get_request_id()}
    payload.update(fields or {})
    log.info("audit", extra=payload)

def audited(action: Optional[str] = None):
    """
    Декоратор для эндпоинтов/сервисов.
    Пример:
        @audited("create_student")
        def create_student(...): ...
    """
    def deco(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            try:
                audit_event(action or fn.__name__, result="ok")
            except Exception:
                # не ломаем основной поток из-за аудита
                pass
            return result
        return wrapper
    return deco
