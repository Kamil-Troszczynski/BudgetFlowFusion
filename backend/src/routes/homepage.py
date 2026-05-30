from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from typing import List


# @app.get("/")
# async def root():
#     return {"message": "BudgetFlowFusion API działa i jest połączone z bazą!"}
 

@app.get("/api/shops", response_model=List[Shop])
def get_all_shops(session: Session = Depends(get_session)):
    shops = session.exec(select(Shop)).all()
    return shops


@app.get("/api/items", response_model=List[Item])
def get_all_items(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return items


@app.get("/api/lists", response_model=List[ShopPurchaseList])
def get_all_lists(session: Session = Depends(get_session)):
    lists = session.exec(select(ShopPurchaseList)).all()
    return lists


@app.get("/api/fundings", response_model=List[Funding])
def get_all_fundings(session: Session = Depends(get_session)):
    fundings = session.exec(select(Funding)).all()
    return fundings


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
