from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class ItemCreate(BaseModel):
    name: str
    link: str
    price: float
    currency: str
    product_subcategory_id: int
    student_id: int


@app.get("/api/items", response_model=List[Item])
def get_all_items(student_id: Optional[int] = None, session: Session = Depends(get_session)):
    if student_id:
        statement = select(Item).where(Item.student_id == student_id)
    else:
        statement = select(Item).where(Item.status == "approved")

    return session.exec(statement).all()


@app.get("/api/items/pending", response_model=List[Item])
def get_pending_items(association_id: Optional[int] = None, session: Session = Depends(get_session)):
    statement = select(Item).where(Item.status == "pending")
    if association_id:
        statement = statement.join(Student).where(Student.association_id == association_id)
    return session.exec(statement).all()


@app.patch("/api/items/{item_id}/approve")
def approve_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        return {"error": "Brak przedmiotu"}
    item.status = "approved"
    session.commit()
    return {"status": "success"}


@app.delete("/api/items/{item_id}/reject")
def reject_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        return {"error": "Brak przedmiotu"}
    session.delete(item)
    session.commit()
    return {"status": "success"}


@app.post("/api/items", response_model=Item)
def create_new_item(item_data: ItemCreate, session: Session = Depends(get_session)):
    first_shop = session.exec(select(Shop)).first()
    if not first_shop:
        return {"error": "Brak sklepów w bazie"}

    student = session.get(Student, item_data.student_id)
    if not student:
        return {"error": "Student nie istnieje"}

    item_status = "approved" if student.project_finance_manager_id else "pending"

    new_item = Item(
        name=item_data.name,
        link=item_data.link,
        price=item_data.price,
        currency=item_data.currency,
        status=item_status,
        created_at=datetime.now(),
        product_subcategory_id=item_data.product_subcategory_id,
        student_id=item_data.student_id,
        shop_id=first_shop.shop_id
    )
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item