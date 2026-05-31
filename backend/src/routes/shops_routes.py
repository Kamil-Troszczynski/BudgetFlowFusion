from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from typing import List


@app.get("/api/shops", response_model=List[Shop])
def get_all_shops(session: Session = Depends(get_session)):
    return session.exec(select(Shop)).all()