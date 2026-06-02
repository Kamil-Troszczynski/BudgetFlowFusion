from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ListCreate(BaseModel):
    priority: int
    cost: float
    created_at: datetime
    funding_id: int
    shop_id: int
    student_id: int

class ListItemCreate(BaseModel):
    item_id: int
    amount: int


@app.get("/api/lists", response_model=List[ShopPurchaseList])
def get_all_lists(student_id: Optional[int] = None, session: Session = Depends(get_session)):
    statement = select(ShopPurchaseList)
    if student_id:
        statement = statement.where(ShopPurchaseList.student_id == student_id)
    statement = statement.order_by(ShopPurchaseList.shop_purchase_list_id.desc())
    return session.exec(statement).all()


@app.post("/api/lists", response_model=ShopPurchaseList)
def create_purchase_list(new_list_data: ListCreate, session: Session = Depends(get_session)):
    new_list = ShopPurchaseList(
        priority=new_list_data.priority,
        cost=new_list_data.cost,
        created_at=new_list_data.created_at,
        funding_id=new_list_data.funding_id,
        shop_id=new_list_data.shop_id,
        student_id=new_list_data.student_id,
        gslbccf_id=1
    )
    session.add(new_list)
    session.commit()
    session.refresh(new_list)
    return new_list


@app.get("/api/lists/{list_id}", response_model=ShopPurchaseList)
def get_single_list(list_id: int, session: Session = Depends(get_session)):
    single_list = session.get(ShopPurchaseList, list_id)
    if not single_list:
        raise HTTPException(status_code=404, detail="Lista nie znaleziona")
    return single_list


@app.delete("/api/lists/{list_id}")
def delete_entire_list(list_id: int, session: Session = Depends(get_session)):
    list_to_delete = session.get(ShopPurchaseList, list_id)
    if not list_to_delete:
        raise HTTPException(status_code=404, detail="Lista nie znaleziona")

    items_on_list = session.exec(
        select(ShopPurchaseListItem).where(ShopPurchaseListItem.shop_purchase_list_id == list_id)
    ).all()

    for item in items_on_list:
        session.delete(item)

    session.delete(list_to_delete)
    session.commit()
    return {"status": "success"}


@app.get("/api/lists/{list_id}/items")
def get_items_for_list(list_id: int, session: Session = Depends(get_session)):
    statement = select(ShopPurchaseListItem).where(ShopPurchaseListItem.shop_purchase_list_id == list_id)
    line_items = session.exec(statement).all()
    results = []
    for line in line_items:
        item_details = session.get(Item, line.item_id)
        if item_details:
            results.append({
                "line_item_id": line.item_id,
                "item_id": item_details.item_id,
                "name": item_details.name,
                "price": item_details.price,
                "currency": item_details.currency,
                "amount": line.amount,
                "total_price": item_details.price * line.amount
            })
    return results


@app.post("/api/lists/{list_id}/items")
def add_item_to_list(list_id: int, item_data: ListItemCreate, session: Session = Depends(get_session)):
    try:
        new_line_item = ShopPurchaseListItem(
            shop_purchase_list_id=list_id,
            item_id=item_data.item_id,
            amount=item_data.amount
        )
        session.add(new_line_item)
        session.commit()
        return {"status": "success", "line_item_id": new_line_item.item_id}
    except Exception as e:
        session.rollback()
        detailed_error = str(e)
        print(f"\n!!! BŁĄD BAZY DANYCH !!!\n{detailed_error}\n")
        raise HTTPException(status_code=400, detail=f"Baza odrzuciła wpis: {detailed_error}")


@app.delete("/api/lists/{list_id}/items/{item_id}")
def remove_item_from_list(list_id: int, item_id: int, session: Session = Depends(get_session)):
    item_to_delete = session.get(ShopPurchaseListItem, (list_id, item_id))
    if not item_to_delete:
        raise HTTPException(status_code=404, detail="Pozycja nie znaleziona")

    session.delete(item_to_delete)
    session.commit()
    return {"status": "success"}