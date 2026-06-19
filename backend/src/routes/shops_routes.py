from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class ShopCreate(BaseModel):
    shop_name: str
    link: Optional[str] = None
    opinion: Optional[str] = None
    free_delivery_threshold: float = 0.0
    student_id: int


class ShopUpdate(BaseModel):
    shop_name: Optional[str] = None
    link: Optional[str] = None
    opinion: Optional[str] = None
    free_delivery_threshold: Optional[float] = None
    student_id: int


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip()


def _normalize_for_compare(value: Optional[str]) -> str:
    return _normalize_text(value).lower()


def _require_treasurer(student_id: int, session: Session) -> Student:
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student nie istnieje")
    if not student.project_finance_manager_id:
        raise HTTPException(status_code=403, detail="Brak uprawnien skarbnika")
    return student


def _ensure_unique_shop(
    session: Session,
    shop_name: Optional[str],
    link: Optional[str],
    current_shop_id: Optional[int] = None,
):
    normalized_name = _normalize_for_compare(shop_name)
    normalized_link = _normalize_for_compare(link)
    shops = session.exec(select(Shop).where(Shop.status != "rejected")).all()

    for shop in shops:
        if current_shop_id and shop.shop_id == current_shop_id:
            continue
        if normalized_name and _normalize_for_compare(shop.shop_name) == normalized_name:
            raise HTTPException(status_code=400, detail="Sklep o tej nazwie juz istnieje")
        if normalized_link and _normalize_for_compare(shop.link) == normalized_link:
            raise HTTPException(status_code=400, detail="Sklep o tym linku juz istnieje")


@app.get("/api/shops", response_model=List[Shop])
def get_all_shops(
    include_pending: bool = False,
    session: Session = Depends(get_session),
):
    statement = select(Shop)
    if include_pending:
        statement = statement.where(Shop.status != "rejected")
    else:
        statement = statement.where(Shop.status == "approved")
    return session.exec(statement.order_by(Shop.shop_name)).all()


@app.post("/api/shops", response_model=Shop)
def create_shop(shop_data: ShopCreate, session: Session = Depends(get_session)):
    student = session.get(Student, shop_data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student nie istnieje")

    shop_name = _normalize_text(shop_data.shop_name)
    link = _normalize_text(shop_data.link) or None
    opinion = _normalize_text(shop_data.opinion) or None

    if not shop_name:
        raise HTTPException(status_code=400, detail="Nazwa sklepu jest wymagana")
    if shop_data.free_delivery_threshold < 0:
        raise HTTPException(status_code=400, detail="Prog darmowej dostawy nie moze byc ujemny")

    _ensure_unique_shop(session, shop_name, link)

    new_shop = Shop(
        shop_name=shop_name,
        link=link,
        opinion=opinion,
        status="pending",
        created_by_student_id=shop_data.student_id,
        address="",
        delivery_time=datetime.now(),
        is_recommended=False,
        free_delivery_threshold=float(shop_data.free_delivery_threshold or 0),
    )
    session.add(new_shop)
    session.commit()
    session.refresh(new_shop)
    return new_shop


@app.patch("/api/shops/{shop_id}", response_model=Shop)
def update_shop(
    shop_id: int,
    shop_data: ShopUpdate,
    session: Session = Depends(get_session),
):
    _require_treasurer(shop_data.student_id, session)
    shop = session.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Sklep nie istnieje")

    next_name = _normalize_text(shop_data.shop_name) if shop_data.shop_name is not None else shop.shop_name
    next_link = _normalize_text(shop_data.link) if shop_data.link is not None else shop.link
    next_link = next_link or None

    if not next_name:
        raise HTTPException(status_code=400, detail="Nazwa sklepu jest wymagana")
    if shop_data.free_delivery_threshold is not None and shop_data.free_delivery_threshold < 0:
        raise HTTPException(status_code=400, detail="Prog darmowej dostawy nie moze byc ujemny")

    _ensure_unique_shop(session, next_name, next_link, current_shop_id=shop_id)

    shop.shop_name = next_name
    shop.link = next_link
    if shop_data.opinion is not None:
        shop.opinion = _normalize_text(shop_data.opinion) or None
    if shop_data.free_delivery_threshold is not None:
        shop.free_delivery_threshold = float(shop_data.free_delivery_threshold)

    session.add(shop)
    session.commit()
    session.refresh(shop)
    return shop


@app.patch("/api/shops/{shop_id}/approve", response_model=Shop)
def approve_shop(
    shop_id: int,
    shop_data: ShopUpdate,
    session: Session = Depends(get_session),
):
    _require_treasurer(shop_data.student_id, session)
    shop = session.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Sklep nie istnieje")

    _ensure_unique_shop(session, shop.shop_name, shop.link, current_shop_id=shop_id)
    shop.status = "approved"
    session.add(shop)
    session.commit()
    session.refresh(shop)
    return shop


@app.delete("/api/shops/{shop_id}/reject")
def reject_shop(
    shop_id: int,
    student_id: int,
    session: Session = Depends(get_session),
):
    _require_treasurer(student_id, session)
    shop = session.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Sklep nie istnieje")
    if shop.status == "approved":
        raise HTTPException(status_code=400, detail="Nie mozna odrzucic zaakceptowanego sklepu")

    shop.status = "rejected"
    session.add(shop)
    session.commit()
    return {"status": "success"}
