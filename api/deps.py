from fastapi import Depends, Query
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import os

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, future=True)

def get_db() -> Session:
    with SessionLocal() as s:
        yield s

class Page:
    def __init__(self, page: int = 1, size: int = 20, max_size: int = 100):
        self.page = max(page, 1)
        self.size = min(max(size, 1), max_size)

def pagination(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> Page:
    return Page(page, size)
