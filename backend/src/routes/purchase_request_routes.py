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


class PurchaseRequestBudgetOut(BaseModel):
    association_budget_id: int
    association_budget_name: str
    total_budget: float
    spent_money: float
    available_money: float
    purchase_requests_total_allocated: float
    available_after_purchase_requests: float


class PurchaseRequestOut(BaseModel):
    purchase_request_id: int
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[int] = None
    association_budget_id: int
    association_budget_name: Optional[str] = None
    created_at: datetime
    can_add: bool
    gslbccf_id: Optional[int] = None
    project_finance_manager_id: Optional[int] = None
    budget_info: Optional[PurchaseRequestBudgetOut] = None


def _budget_info_for_request(request: PurchaseRequest, session: Session) -> Optional[PurchaseRequestBudgetOut]:
    budget = session.get(AssociationBudget, request.association_budget_id)
    if not budget:
        return None

    purchase_requests = session.exec(
        select(PurchaseRequest).where(
            PurchaseRequest.association_budget_id == budget.association_budget_id
        )
    ).all()
    total_allocated = sum(
        purchase_request.budget_allocated_for_the_order
        for purchase_request in purchase_requests
    )

    available_money = budget.total_budget - budget.spent_money
    return PurchaseRequestBudgetOut(
        association_budget_id=budget.association_budget_id,
        association_budget_name=budget.association_budget_name,
        total_budget=budget.total_budget,
        spent_money=budget.spent_money,
        available_money=available_money,
        purchase_requests_total_allocated=total_allocated,
        available_after_purchase_requests=available_money - total_allocated,
    )


def _purchase_request_out(request: PurchaseRequest, session: Session) -> PurchaseRequestOut:
    budget_info = _budget_info_for_request(request, session)
    return PurchaseRequestOut(
        purchase_request_id=request.purchase_request_id,
        purchase_request_name=request.purchase_request_name,
        budget_allocated_for_the_order=request.budget_allocated_for_the_order,
        if_service=request.if_service,
        used_cpv_id=request.used_cpv_id,
        association_budget_id=request.association_budget_id,
        association_budget_name=budget_info.association_budget_name if budget_info else None,
        created_at=request.created_at,
        can_add=request.can_add,
        gslbccf_id=request.gslbccf_id,
        project_finance_manager_id=request.project_finance_manager_id,
        budget_info=budget_info,
    )


@app.get("/api/purchase_requests/detail/{purchase_request_id}", response_model=PurchaseRequestOut)
def get_single_purchase_request(purchase_request_id: int, session: Session = Depends(get_session)):
    purchase_request = session.exec(
        select(PurchaseRequest).where(PurchaseRequest.purchase_request_id == purchase_request_id)
    ).first()    
    if not purchase_request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
        
    return _purchase_request_out(purchase_request, session)


@app.get("/api/purchase_requests", response_model=List[PurchaseRequestOut])
def get_purchase_requests(session: Session = Depends(get_session)):
    statement = select(PurchaseRequest)
    purchase_requests = session.exec(statement).all()
    return [_purchase_request_out(purchase_request, session) for purchase_request in purchase_requests]


@app.get("/api/purchase_requests/{project_finance_manager_id}", response_model=List[PurchaseRequestOut])
def get_purchase_requests_by_project_finance_manager(project_finance_manager_id: int, 
                                                     session: Session = Depends(get_session)):
    statement = select(PurchaseRequest).where(PurchaseRequest.project_finance_manager_id == project_finance_manager_id)
    purchase_requests = session.exec(statement).all()
    return [_purchase_request_out(purchase_request, session) for purchase_request in purchase_requests]


@app.post("/api/create_purchase_requests", response_model=PurchaseRequestOut)
def create_purchase_request(new_purchase_request_data: PurchaseRequestCreate, session: Session = Depends(get_session)):
    association_budget = session.get(AssociationBudget, new_purchase_request_data.association_budget_id)
    if not association_budget:
        raise HTTPException(status_code=404, detail="Budżet koła nie znaleziony")

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
    return _purchase_request_out(new_purchase_request, session)


@app.delete("/api/purchase_requests/{purchase_request_id}")
def delete_purchase_request(purchase_request_id: int, session: Session = Depends(get_session)):
    purchase_request = session.exec(select(PurchaseRequest).where(PurchaseRequest.purchase_request_id == purchase_request_id)).first()
    if not purchase_request:
        raise HTTPException(status_code = 404, detail = "Wniosek nie znaleziony")
    session.delete(purchase_request)
    session.commit()
    return {"message": "Wniosek usunięty pomyślnie"}
