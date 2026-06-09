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


class GroupedItemOut(BaseModel):
    item_id: int
    name: str
    price: float
    currency: str
    link: Optional[str] = None
    status: str
    shop_name: Optional[str] = None
    category_name: Optional[str] = None
    cpv: Optional[str] = None
    student_id: int


class ItemGroupOut(BaseModel):
    group_key: str
    group_label: str
    count: int
    total_price: float
    items: List[GroupedItemOut]


def _item_group_metadata(item: Item, session: Session):
    shop = session.get(Shop, item.shop_id) if item.shop_id else None
    subcategory = (
        session.get(ProductSubcategory, item.product_subcategory_id)
        if item.product_subcategory_id
        else None
    )
    category = (
        session.get(ProductCategory, subcategory.product_category_id)
        if subcategory and subcategory.product_category_id
        else None
    )
    return shop, subcategory, category


@app.get("/api/items/grouped", response_model=List[ItemGroupOut])
def get_grouped_items(
    group_by: str = "shop",
    student_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    allowed_groups = {"shop", "cpv", "category", "status"}
    if group_by not in allowed_groups:
        group_by = "shop"

    statement = select(Item)
    if student_id:
        statement = statement.where(Item.student_id == student_id)
    else:
        statement = statement.where(Item.status == "approved")

    items = session.exec(statement).all()
    groups = {}

    for item in items:
        shop, subcategory, category = _item_group_metadata(item, session)

        if group_by == "shop":
            key = str(item.shop_id or "none")
            label = shop.shop_name if shop else "Brak sklepu"
        elif group_by == "cpv":
            key = category.cpv if category and category.cpv else "none"
            label = f"CPV: {key}" if key != "none" else "Brak CPV"
        elif group_by == "category":
            key = str(category.product_category_id) if category else "none"
            label = category.product_category_name if category else "Brak kategorii"
        else:
            key = item.status or "none"
            label = item.status or "Brak statusu"

        if key not in groups:
            groups[key] = {
                "group_key": key,
                "group_label": label,
                "items": [],
            }

        groups[key]["items"].append(
            GroupedItemOut(
                item_id=item.item_id,
                name=item.name,
                price=item.price,
                currency=item.currency,
                link=item.link,
                status=item.status,
                shop_name=shop.shop_name if shop else None,
                category_name=category.product_category_name if category else None,
                cpv=category.cpv if category else None,
                student_id=item.student_id,
            )
        )

    result = []
    for group in groups.values():
        grouped_items = group["items"]
        result.append(
            ItemGroupOut(
                group_key=group["group_key"],
                group_label=group["group_label"],
                count=len(grouped_items),
                total_price=sum(item.price for item in grouped_items),
                items=grouped_items,
            )
        )

    return sorted(result, key=lambda group: group.group_label)


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
