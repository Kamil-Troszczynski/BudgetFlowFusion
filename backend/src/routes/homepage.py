from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException

class LoginRequest(BaseModel):
    email: str
    password: str

class ItemCreate(BaseModel):
    name: str
    link: str
    price: float
    currency: str
    product_subcategory_id: int
    student_id: int

class CategoryCreate(BaseModel):
    name: str
    cpv: str

class SubcategoryCreate(BaseModel):
    name: str
    product_category_id: int

@app.get("/api/shops", response_model=List[Shop])
def get_all_shops(session: Session = Depends(get_session)):
    return session.exec(select(Shop)).all()

@app.get("/api/fundings", response_model=List[Funding])
def get_all_fundings(association_id: Optional[int] = None, session: Session = Depends(get_session)):
    statement = select(Funding)
    if association_id:
        statement = statement.join(Project).where(Project.association_id == association_id)
    return session.exec(statement).all()

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

@app.get("/api/items", response_model=List[Item])
def get_all_items(session: Session = Depends(get_session)):
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

@app.get("/api/categories")
def get_categories(session: Session = Depends(get_session)):
    return session.exec(select(ProductCategory)).all()

@app.post("/api/categories")
def create_category(cat_data: CategoryCreate, session: Session = Depends(get_session)):
    new_cat = ProductCategory(
        product_category_name=cat_data.name,
        description="",
        cpv=cat_data.cpv
    )
    session.add(new_cat)
    session.commit()
    session.refresh(new_cat)
    return new_cat

@app.get("/api/subcategories")
def get_subcategories(session: Session = Depends(get_session)):
    return session.exec(select(ProductSubcategory)).all()

@app.post("/api/subcategories")
def create_subcategory(subcat_data: SubcategoryCreate, session: Session = Depends(get_session)):
    new_subcat = ProductSubcategory(
        product_subcategory_name=subcat_data.name,
        description="",
        product_category_id=subcat_data.product_category_id
    )
    session.add(new_subcat)
    session.commit()
    session.refresh(new_subcat)
    return new_subcat

@app.post("/api/login")
def login_user(credentials: LoginRequest, session: Session = Depends(get_session)):
    statement = select(Student).where(Student.login == credentials.email)
    user = session.exec(statement).first()

    if not user or user.password_hash != credentials.password:
        raise HTTPException(status_code=401, detail="Nieprawidłowy email lub hasło")

    return {
        "id": user.student_id,
        "firstName": user.name,
        "lastName": user.surname,
        "email": user.login,
        "circleName": user.association.association_name if user.association else "Brak koła",
        "association_id": user.association_id,
        "position": user.position,
        "inSAP": user.is_in_sap,
        "role": "treasurer" if user.project_finance_manager_id else "member"
    }