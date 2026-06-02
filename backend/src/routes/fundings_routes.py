from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from typing import List, Optional



@app.get("/api/fundings", response_model=List[Funding])
def get_all_fundings(association_id: Optional[int] = None, session: Session = Depends(get_session)):
    statement = select(Funding)
    if association_id:
        statement = statement.join(Project).where(Project.association_id == association_id)
    return session.exec(statement).all()