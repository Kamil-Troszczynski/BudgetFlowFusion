from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from typing import List, Optional


@app.get("/api/lists", response_model=List[ShopPurchaseList])
def get_all_lists(student_id: Optional[int] = None, session: Session = Depends(get_session)):
    statement = select(ShopPurchaseList)
    if student_id:
        statement = statement.where(ShopPurchaseList.student_id == student_id)
    return session.exec(statement).all()


@app.post("/api/lists", response_model=ShopPurchaseList)
def create_purchase_list(new_list: ShopPurchaseList, session: Session = Depends(get_session)):
    session.add(new_list)
    session.commit()
    session.refresh(new_list)
    return new_list


@app.get("/api/lists/{list_id}/items")
def get_items_for_list(list_id: int, session: Session = Depends(get_session)):
    statement = select(ShopPurchaseListItem).where(ShopPurchaseListItem.shop_purchase_list_id == list_id)
    line_items = session.exec(statement).all()
    results = []
    for line in line_items:
        item_details = session.get(Item, line.item_id)
        if item_details:
            results.append({
                "line_item_id": line.shop_purchase_list_item_id,
                "item_id": item_details.item_id,
                "name": item_details.name,
                "price": item_details.price,
                "currency": item_details.currency,
                "amount": line.amount,
                "total_price": item_details.price * line.amount
            })
    return results


@app.post("/api/lists/{list_id}/items")
def add_item_to_list(list_id: int, item_id: int, amount: int, session: Session = Depends(get_session)):
    new_line_item = ShopPurchaseListItem(
        shop_purchase_list_id=list_id,
        item_id=item_id,
        amount=amount
    )
    session.add(new_line_item)
    session.commit()
    session.refresh(new_line_item)
    return {"status": "success", "line_item_id": new_line_item.shop_purchase_list_item_id}


@app.delete("/api/lists/items/{line_item_id}")
def remove_item_from_list(line_item_id: int, session: Session = Depends(get_session)):
    item_to_delete = session.get(ShopPurchaseListItem, line_item_id)
    if not item_to_delete:
        return {"error": "Pozycja nie znaleziona"}
    session.delete(item_to_delete)
    session.commit()
    return {"status": "success"}