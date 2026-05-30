from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from typing import List

from database import create_db_and_tables, get_session
from src.relations import Shop, Item, ShopPurchaseList, Funding

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "BudgetFlowFusion API działa i jest połączone z bazą!"}

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
