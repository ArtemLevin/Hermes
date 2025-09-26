from __future__ import annotations
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from deps import get_db, pagination, Page
from models import Student, Invoice, Payment  # добавьте модели в models.py при необходимости
from jobs import enqueue_invoice_due
from audit import audit_event

router = APIRouter()

# ==== Pydantic ====
class InvoiceCreateIn(BaseModel):
    student_id: int
    amount: Decimal
    due_date: Optional[date] = None
    notes: Optional[str] = None

class InvoiceOut(BaseModel):
    id: int
    student_id: int
    amount: Decimal
    status: str
    due_date: Optional[date] = None
    created_at: datetime
    notes: Optional[str] = None

class PaymentCreateIn(BaseModel):
    student_id: int
    invoice_id: Optional[int] = None
    amount: Decimal
    method: Optional[str] = "cash"  # cash|transfer|card

class PaymentOut(BaseModel):
    id: int
    student_id: int
    invoice_id: Optional[int]
    amount: Decimal
    status: str
    method: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime

# ==== Endpoints: INVOICES ====
@router.get("/invoices")
def list_invoices(
    db: Session = Depends(get_db),
    page: Page = Depends(pagination),
    student_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
):
    stmt = select(Invoice)
    if student_id:
        stmt = stmt.where(Invoice.student_id == student_id)
    if status:
        stmt = stmt.where(Invoice.status == status)
    rows = db.execute(stmt.order_by(Invoice.created_at.desc())).scalars().all()
    total = len(rows)
    start = (page.page - 1) * page.size
    items = rows[start : start + page.size]
    return {
        "total": total,
        "items": [
            {
                "id": x.id,
                "student_id": x.student_id,
                "amount": x.amount,
                "status": x.status,
                "due_date": x.due_date,
                "created_at": x.created_at,
                "notes": x.notes,
            }
            for x in items
        ],
    }

@router.post("/invoices", response_model=InvoiceOut)
def create_invoice(payload: InvoiceCreateIn, db: Session = Depends(get_db)):
    if not db.get(Student, payload.student_id):
        raise HTTPException(404, "Student not found")
    inv = Invoice(
        student_id=payload.student_id,
        amount=payload.amount,
        status="issued",
        due_date=payload.due_date,
        notes=payload.notes,
        created_at=datetime.utcnow(),
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # Планируем напоминание за 3 дня до due_date (если есть)
    if inv.due_date:
        enqueue_invoice_due(
            payer_email=f"parent+{inv.student_id}@example.com",  # TODO: реальный email родителя
            invoice_id=inv.id,
            amount=float(inv.amount),
            due_date=datetime.combine(inv.due_date, datetime.min.time()),
        )

    audit_event("create_invoice", invoice_id=inv.id, student_id=inv.student_id, amount=float(inv.amount))
    return InvoiceOut(
        id=inv.id,
        student_id=inv.student_id,
        amount=inv.amount,
        status=inv.status,
        due_date=inv.due_date,
        created_at=inv.created_at,
        notes=inv.notes,
    )

@router.post("/invoices/{invoice_id}/mark_paid", response_model=InvoiceOut)
def mark_invoice_paid(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    inv.status = "paid"
    db.commit()
    audit_event("mark_invoice_paid", invoice_id=inv.id, student_id=inv.student_id)
    return InvoiceOut(
        id=inv.id,
        student_id=inv.student_id,
        amount=inv.amount,
        status=inv.status,
        due_date=inv.due_date,
        created_at=inv.created_at,
        notes=inv.notes,
    )

# ==== Endpoints: PAYMENTS ====
@router.get("/payments")
def list_payments(
    db: Session = Depends(get_db),
    page: Page = Depends(pagination),
    student_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
):
    stmt = select(Payment)
    if student_id:
        stmt = stmt.where(Payment.student_id == student_id)
    if status:
        stmt = stmt.where(Payment.status == status)
    rows = db.execute(stmt.order_by(Payment.created_at.desc())).scalars().all()
    total = len(rows)
    start = (page.page - 1) * page.size
    items = rows[start : start + page.size]
    return {
        "total": total,
        "items": [
            {
                "id": x.id,
                "student_id": x.student_id,
                "invoice_id": x.invoice_id,
                "amount": x.amount,
                "status": x.status,
                "method": x.method,
                "paid_at": x.paid_at,
                "created_at": x.created_at,
            }
            for x in items
        ],
    }

@router.post("/payments", response_model=PaymentOut)
def create_payment(payload: PaymentCreateIn, db: Session = Depends(get_db)):
    if not db.get(Student, payload.student_id):
        raise HTTPException(404, "Student not found")

    p = Payment(
        student_id=payload.student_id,
        invoice_id=payload.invoice_id,
        amount=payload.amount,
        status="paid",  # в MVP — сразу считаем оплачено (ручной учёт)
        method=payload.method,
        paid_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    db.add(p)

    # Если указан инвойс — отметим его как оплаченный
    if payload.invoice_id:
        inv = db.get(Invoice, payload.invoice_id)
        if inv:
            inv.status = "paid"

    db.commit()
    db.refresh(p)
    audit_event(
        "create_payment",
        payment_id=p.id,
        student_id=p.student_id,
        invoice_id=p.invoice_id,
        amount=float(p.amount),
        method=p.method,
    )
    return PaymentOut(
        id=p.id,
        student_id=p.student_id,
        invoice_id=p.invoice_id,
        amount=p.amount,
        status=p.status,
        method=p.method,
        paid_at=p.paid_at,
        created_at=p.created_at,
    )
