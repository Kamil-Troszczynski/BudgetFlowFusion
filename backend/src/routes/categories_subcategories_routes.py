from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    cpv: str


class SubcategoryCreate(BaseModel):
    name: str
    product_category_id: int


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