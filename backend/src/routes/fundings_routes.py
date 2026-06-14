from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from typing import List, Optional
from pydantic import BaseModel


class FundingOut(BaseModel):
    funding_id: int
    funding_name: str
    funding_price: float
    spent_money: float
    available_money: float
    purchase_requests_total_allocated: float
    available_after_purchase_requests: float
    project_id: Optional[int] = None
    project_budget_id: int
    project_budget_name: Optional[str] = None


@app.get("/api/fundings", response_model=List[FundingOut])
def get_all_fundings(association_id: Optional[int] = None, session: Session = Depends(get_session)):
    statement = select(Funding)
    if association_id:
        statement = (
            statement
            .join(ProjectBudget)
            .join(Project)
            .where(Project.association_id == association_id)
        )
    fundings = session.exec(statement).all()
    result = []
    for funding in fundings:
        project_budget = session.get(ProjectBudget, funding.project_budget_id)
        purchase_requests = session.exec(
            select(PurchaseRequest).where(PurchaseRequest.funding_id == funding.funding_id)
        ).all()
        allocated = sum(
            request.budget_allocated_for_the_order for request in purchase_requests
        )
        result.append(FundingOut(
            funding_id=funding.funding_id,
            funding_name=funding.funding_name,
            funding_price=funding.funding_price,
            spent_money=funding.spent_money,
            available_money=funding.funding_price - funding.spent_money,
            purchase_requests_total_allocated=allocated,
            available_after_purchase_requests=(
                funding.funding_price - funding.spent_money - allocated
            ),
            project_id=funding.project_id,
            project_budget_id=funding.project_budget_id,
            project_budget_name=(
                project_budget.project_budget_name if project_budget else None
            ),
        ))
    return result
