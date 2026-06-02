from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime



class PurchaseRequestCreate(BaseModel):
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[int]
    association_budget_id: int
    created_at: datetime
    created_by_user_id: Optional[int] = None
    can_add: bool = True
    project_finance_manager_id: int


@app.get("/api/purchase_requests/detail/{purchase_request_id}", response_model=PurchaseRequest)
def get_single_purchase_request(purchase_request_id: int, session: Session = Depends(get_session)):
    purchase_request = session.exec(
        select(PurchaseRequest).where(PurchaseRequest.purchase_request_id == purchase_request_id)
    ).first()    
    if not purchase_request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
        
    return purchase_request


@app.get("/api/purchase_requests", response_model=List[PurchaseRequest])
def get_purchase_requests(session: Session = Depends(get_session)):
    statement = select(PurchaseRequest)
    return session.exec(statement).all()


@app.get("/api/purchase_requests/{project_finance_manager_id}", response_model=List[PurchaseRequest])
def get_purchase_requests_by_project_finance_manager(project_finance_manager_id: int, 
                                                     session: Session = Depends(get_session)):
    statement = select(PurchaseRequest).where(PurchaseRequest.project_finance_manager_id == project_finance_manager_id)
    return session.exec(statement).all()


@app.post("/api/create_purchase_requests", response_model=PurchaseRequest)
def create_purchase_request(new_purchase_request_data: PurchaseRequestCreate, session: Session = Depends(get_session)):
    new_purchase_request = PurchaseRequest(
        purchase_request_name = new_purchase_request_data.purchase_request_name,
        budget_allocated_for_the_order = new_purchase_request_data.budget_allocated_for_the_order,
        if_service = new_purchase_request_data.if_service,
        used_cpv_id = new_purchase_request_data.used_cpv_id,
        association_budget_id = new_purchase_request_data.association_budget_id,
        created_at = new_purchase_request_data.created_at,
        can_add = new_purchase_request_data.can_add,
        project_finance_manager_id = new_purchase_request_data.project_finance_manager_id
    )
    session.add(new_purchase_request)
    session.commit()
    session.refresh(new_purchase_request)
    return new_purchase_request


@app.delete("/api/purchase_requests/{purchase_request_id}")
def delete_purchase_request(purchase_request_id: int, session: Session = Depends(get_session)):
    purchase_request = session.exec(select(PurchaseRequest).where(PurchaseRequest.purchase_request_id == purchase_request_id)).first()
    if not purchase_request:
        raise HTTPException(status_code = 404, detail = "Wniosek nie znaleziony")
    session.delete(purchase_request)
    session.commit()
    return {"message": "Wniosek usunięty pomyślnie"}
