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
    tax_rate: Optional[float] = 23


class GroupedItemOut(BaseModel):
    item_id: int
    name: str
    price: float
    currency: str
    link: Optional[str] = None
    status: str
    shop_name: Optional[str] = None
    subcategory_name: Optional[str] = None
    category_name: Optional[str] = None
    cpv: Optional[str] = None
    project_names: List[str] = []
    student_id: int
    created_at: Optional[datetime] = None


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


def _item_project_names(item: Item, session: Session) -> List[str]:
    list_items = session.exec(
        select(ShopPurchaseListItem).where(ShopPurchaseListItem.item_id == item.item_id)
    ).all()
    project_names = []

    for list_item in list_items:
        shopping_list = session.get(
            ShopPurchaseList, list_item.shop_purchase_list_id
        )
        funding = (
            session.get(Funding, shopping_list.funding_id)
            if shopping_list and shopping_list.funding_id
            else None
        )
        project_budget = (
            session.get(ProjectBudget, funding.project_budget_id)
            if funding and funding.project_budget_id
            else None
        )
        project = (
            session.get(Project, project_budget.project_id)
            if project_budget and project_budget.project_id
            else session.get(Project, funding.project_id)
            if funding and funding.project_id
            else None
        )

        if project and project.project_name not in project_names:
            project_names.append(project.project_name)

    return project_names


@app.get("/api/items/grouped", response_model=List[ItemGroupOut])
def get_grouped_items(
    group_by: str = "shop",
    session: Session = Depends(get_session),
):
    allowed_groups = {"shop", "cpv", "category", "status"}
    if group_by not in allowed_groups:
        group_by = "shop"

    statement = select(Item).where(Item.status == "approved")

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
                subcategory_name=subcategory.product_subcategory_name if subcategory else None,
                category_name=category.product_category_name if category else None,
                cpv=category.cpv if category else None,
                project_names=_item_project_names(item, session),
                student_id=item.student_id,
                created_at=item.created_at,
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


@app.get("/api/items", response_model=List[GroupedItemOut])
def get_all_items(session: Session = Depends(get_session)):
    statement = select(Item).where(Item.status == "approved")
    items = session.exec(statement.order_by(Item.created_at.desc())).all()
    result = []
    for item in items:
        shop, subcategory, category = _item_group_metadata(item, session)
        result.append(GroupedItemOut(
            item_id=item.item_id,
            name=item.name,
            price=item.price,
            currency=item.currency,
            link=item.link,
            status=item.status,
            shop_name=shop.shop_name if shop else None,
            subcategory_name=subcategory.product_subcategory_name if subcategory else None,
            category_name=category.product_category_name if category else None,
            cpv=category.cpv if category else None,
            project_names=_item_project_names(item, session),
            student_id=item.student_id,
            created_at=item.created_at,
        ))
    return result


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

    new_item = Item(
        name=item_data.name,
        link=item_data.link,
        price=item_data.price,
        currency=item_data.currency,
        tax_rate=float(item_data.tax_rate if item_data.tax_rate is not None else 23),
        status="approved",
        created_at=datetime.now(),
        product_subcategory_id=item_data.product_subcategory_id,
        student_id=item_data.student_id,
        shop_id=first_shop.shop_id
    )
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item
