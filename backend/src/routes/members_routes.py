from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from typing import List



@app.get("/api/students", response_model=List[Student])
def get_all_student(session: Session = Depends(get_session)):
    statement = select(Student)
    return session.exec(statement).all()