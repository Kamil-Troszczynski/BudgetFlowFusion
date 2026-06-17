from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field as PydanticField


class FundingTaskIn(BaseModel):
    task_name: str
    task_budget: float


class FundingCreate(BaseModel):
    funding_name: str
    organizer: str
    signing_person: str
    funding_price: float
    project_budget_id: int
    tasks: List[FundingTaskIn] = PydanticField(default_factory=list)


class FundingUpdate(FundingCreate):
    pass


class FundingTaskOut(BaseModel):
    funding_task_id: int
    task_name: str
    task_budget: float


class FundingOut(BaseModel):
    funding_id: int
    funding_name: str
    organizer: Optional[str] = None
    signing_person: Optional[str] = None
    funding_price: float
    spent_money: float
    available_money: float
    purchase_requests_total_allocated: float
    available_after_purchase_requests: float
    project_id: Optional[int] = None
    project_budget_id: int
    project_budget_name: Optional[str] = None
    tasks: List[FundingTaskOut] = PydanticField(default_factory=list)


def _funding_out(funding: Funding, session: Session) -> FundingOut:
    project_budget = session.get(ProjectBudget, funding.project_budget_id)
    allocation_rows = session.exec(
        select(PurchaseRequestFundingAllocation).where(
            PurchaseRequestFundingAllocation.funding_id == funding.funding_id
        )
    ).all()
    allocated_request_ids = {allocation.purchase_request_id for allocation in allocation_rows}
    purchase_requests = session.exec(
        select(PurchaseRequest).where(PurchaseRequest.funding_id == funding.funding_id)
    ).all()
    allocated = sum(allocation.allocated_amount for allocation in allocation_rows)
    allocated += sum(
        request.budget_allocated_for_the_order
        for request in purchase_requests
        if request.purchase_request_id not in allocated_request_ids
    )
    tasks = session.exec(
        select(FundingTask).where(FundingTask.funding_id == funding.funding_id)
    ).all()
    return FundingOut(
        funding_id=funding.funding_id,
        funding_name=funding.funding_name,
        organizer=funding.organizer,
        signing_person=funding.signing_person,
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
        tasks=[
            FundingTaskOut(
                funding_task_id=task.funding_task_id,
                task_name=task.task_name,
                task_budget=task.task_budget,
            )
            for task in tasks
        ],
    )


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
    return [_funding_out(funding, session) for funding in fundings]


@app.post("/api/fundings", response_model=FundingOut)
def create_funding(
    funding_data: FundingCreate,
    session: Session = Depends(get_session),
):
    funding_name = (funding_data.funding_name or "").strip()
    organizer = (funding_data.organizer or "").strip()
    signing_person = (funding_data.signing_person or "").strip()
    if not funding_name:
        raise HTTPException(status_code=400, detail="Nazwa dofinansowania jest wymagana")
    if not organizer:
        raise HTTPException(status_code=400, detail="Organizator jest wymagany")
    if not signing_person:
        raise HTTPException(status_code=400, detail="Osoba podpisujaca jest wymagana")
    if funding_data.funding_price <= 0:
        raise HTTPException(status_code=400, detail="Kwota dofinansowania musi byc wieksza od zera")

    project_budget = session.get(ProjectBudget, funding_data.project_budget_id)
    if not project_budget:
        raise HTTPException(status_code=404, detail="Sekcja/projekt nie znaleziony")

    prepared_tasks: list[FundingTaskIn] = []
    tasks_total = 0.0
    for task in funding_data.tasks:
        task_name = (task.task_name or "").strip()
        task_budget = float(task.task_budget or 0)
        if not task_name:
            raise HTTPException(status_code=400, detail="Nazwa zadania jest wymagana")
        if task_budget <= 0:
            raise HTTPException(status_code=400, detail="Budzet zadania musi byc wiekszy od zera")
        tasks_total += task_budget
        prepared_tasks.append(FundingTaskIn(task_name=task_name, task_budget=task_budget))
    if tasks_total > funding_data.funding_price:
        raise HTTPException(status_code=400, detail="Suma zadan nie moze przekraczac kwoty dofinansowania")

    funding = Funding(
        funding_name=funding_name,
        organizer=organizer,
        signing_person=signing_person,
        funding_price=funding_data.funding_price,
        spent_money=0.0,
        project_id=project_budget.project_id,
        project_budget_id=project_budget.project_budget_id,
        association_budget_id=project_budget.association_budget_id,
    )
    session.add(funding)
    session.flush()
    for task in prepared_tasks:
        session.add(FundingTask(
            funding_id=funding.funding_id,
            task_name=task.task_name,
            task_budget=task.task_budget,
        ))
    session.commit()
    session.refresh(funding)
    return _funding_out(funding, session)


@app.patch("/api/fundings/{funding_id}", response_model=FundingOut)
def update_funding(
    funding_id: int,
    funding_data: FundingUpdate,
    session: Session = Depends(get_session),
):
    funding = session.get(Funding, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Dofinansowanie nie znalezione")

    funding_name = (funding_data.funding_name or "").strip()
    organizer = (funding_data.organizer or "").strip()
    signing_person = (funding_data.signing_person or "").strip()
    if not funding_name:
        raise HTTPException(status_code=400, detail="Nazwa dofinansowania jest wymagana")
    if not organizer:
        raise HTTPException(status_code=400, detail="Organizator jest wymagany")
    if not signing_person:
        raise HTTPException(status_code=400, detail="Osoba podpisujaca jest wymagana")
    if funding_data.funding_price <= 0:
        raise HTTPException(status_code=400, detail="Kwota dofinansowania musi byc wieksza od zera")

    project_budget = session.get(ProjectBudget, funding_data.project_budget_id)
    if not project_budget:
        raise HTTPException(status_code=404, detail="Sekcja/projekt nie znaleziony")

    prepared_tasks: list[FundingTaskIn] = []
    tasks_total = 0.0
    for task in funding_data.tasks:
        task_name = (task.task_name or "").strip()
        task_budget = float(task.task_budget or 0)
        if not task_name:
            raise HTTPException(status_code=400, detail="Nazwa zadania jest wymagana")
        if task_budget <= 0:
            raise HTTPException(status_code=400, detail="Budzet zadania musi byc wiekszy od zera")
        tasks_total += task_budget
        prepared_tasks.append(FundingTaskIn(task_name=task_name, task_budget=task_budget))
    if tasks_total > funding_data.funding_price:
        raise HTTPException(status_code=400, detail="Suma zadan nie moze przekraczac kwoty dofinansowania")

    funding.funding_name = funding_name
    funding.organizer = organizer
    funding.signing_person = signing_person
    funding.funding_price = funding_data.funding_price
    funding.project_id = project_budget.project_id
    funding.project_budget_id = project_budget.project_budget_id
    funding.association_budget_id = project_budget.association_budget_id
    session.add(funding)

    existing_tasks = session.exec(
        select(FundingTask).where(FundingTask.funding_id == funding.funding_id)
    ).all()
    for task in existing_tasks:
        session.delete(task)
    for task in prepared_tasks:
        session.add(FundingTask(
            funding_id=funding.funding_id,
            task_name=task.task_name,
            task_budget=task.task_budget,
        ))

    session.commit()
    session.refresh(funding)
    return _funding_out(funding, session)
