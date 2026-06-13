from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field as PydanticField


class FundingOut(BaseModel):
    funding_id: int
    funding_name: str
    funding_price: float
    spent_money: float
    available_money: float
    project_id: Optional[int] = None


class PublicPurchasePlanOut(BaseModel):
    public_purchase_plan_id: int
    public_purchase_plan_name: str
    cost: float
    funding_id: Optional[int] = None
    funding_name: Optional[str] = None
    public_purchase_plan_list_id: int


class PublicPurchasePlanListOut(BaseModel):
    public_purchase_plan_list_id: int
    public_plan_list_name: str
    public_purchase_plans: List[PublicPurchasePlanOut] = PydanticField(default_factory=list)
    total_cost: float = 0.0


class PurchaseRequestForBudgetOut(BaseModel):
    purchase_request_id: int
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[int] = None
    created_at: Optional[str] = None
    can_add: bool
    project_finance_manager_id: Optional[int] = None
    project_budget_id: int


class ProjectBudgetOut(BaseModel):
    project_budget_id: int
    project_budget_name: str
    total_budget: float
    spent_money: float
    purchase_requests_total_allocated: float
    available_after_purchase_requests: float
    association_budget_id: int
    association_budget_name: Optional[str] = None
    project_id: int
    project_name: Optional[str] = None


class DashboardBudgetSummaryOut(BaseModel):
    total_budget: float
    spent_money: float
    purchase_requests_total_allocated: float
    available_after_purchase_requests: float


class AssociationBudgetOut(BaseModel):
    association_budget_id: int
    association_budget_name: str
    total_budget: float
    spent_money: float
    available_money: float
    purchase_requests_total_allocated: float = 0.0
    available_after_purchase_requests: float = 0.0
    public_purchase_plan_list_id: Optional[int] = None
    public_purchase_plan_list: Optional[PublicPurchasePlanListOut] = None
    fundings: List[FundingOut] = PydanticField(default_factory=list)
    purchase_requests: List[PurchaseRequestForBudgetOut] = PydanticField(default_factory=list)


class PublicPurchasePlanListCreate(BaseModel):
    association_budget_id: int
    public_plan_list_name: str


class PublicPurchasePlanCreate(BaseModel):
    public_purchase_plan_list_id: int
    public_purchase_plan_name: str
    cost: float
    funding_id: int


def _funding_out(funding: Funding) -> FundingOut:
    return FundingOut(
        funding_id=funding.funding_id,
        funding_name=funding.funding_name,
        funding_price=funding.funding_price,
        spent_money=funding.spent_money,
        available_money=funding.funding_price - funding.spent_money,
        project_id=funding.project_id,
    )


def _get_funding_name_by_id(session: Session, funding_ids: set[int]) -> dict[int, str]:
    if not funding_ids:
        return {}

    fundings = session.exec(
        select(Funding).where(Funding.funding_id.in_(list(funding_ids)))
    ).all()
    return {funding.funding_id: funding.funding_name for funding in fundings}


def _plan_list_out(plan_list: PublicPurchasePlanList, session: Session) -> PublicPurchasePlanListOut:
    plans = session.exec(
        select(PublicPurchasePlan)
        .where(PublicPurchasePlan.public_purchase_plan_list_id == plan_list.public_purchase_plan_list_id)
        .order_by(PublicPurchasePlan.public_purchase_plan_id.desc())
    ).all()
    funding_names = _get_funding_name_by_id(
        session,
        {plan.funding_id for plan in plans if plan.funding_id is not None},
    )
    public_plans = [
        PublicPurchasePlanOut(
            public_purchase_plan_id=plan.public_purchase_plan_id,
            public_purchase_plan_name=plan.public_purchase_plan_name,
            cost=plan.cost,
            funding_id=plan.funding_id,
            funding_name=funding_names.get(plan.funding_id),
            public_purchase_plan_list_id=plan.public_purchase_plan_list_id,
        )
        for plan in plans
    ]

    return PublicPurchasePlanListOut(
        public_purchase_plan_list_id=plan_list.public_purchase_plan_list_id,
        public_plan_list_name=plan_list.public_plan_list_name,
        public_purchase_plans=public_plans,
        total_cost=sum(plan.cost for plan in plans),
    )


def _get_budget_fundings(
    budget_id: int,
    session: Session,
    association_id: Optional[int] = None,
) -> List[Funding]:
    statement = select(Funding).where(Funding.association_budget_id == budget_id)
    if association_id:
        statement = statement.join(Project).where(Project.association_id == association_id)
    return session.exec(statement).all()


def _budget_out(
    budget: AssociationBudget,
    session: Session,
    association_id: Optional[int] = None,
) -> AssociationBudgetOut:
    fundings = _get_budget_fundings(budget.association_budget_id, session, association_id)
    purchase_requests = session.exec(
        select(PurchaseRequest)
        .join(ProjectBudget)
        .where(ProjectBudget.association_budget_id == budget.association_budget_id)
        .order_by(PurchaseRequest.created_at.desc())
    ).all()
    purchase_requests_total = sum(
        purchase_request.budget_allocated_for_the_order
        for purchase_request in purchase_requests
    )
    available_money = budget.total_budget - budget.spent_money
    plan_list = (
        session.get(PublicPurchasePlanList, budget.public_purchase_plan_list_id)
        if budget.public_purchase_plan_list_id
        else None
    )

    return AssociationBudgetOut(
        association_budget_id=budget.association_budget_id,
        association_budget_name=budget.association_budget_name,
        total_budget=budget.total_budget,
        spent_money=budget.spent_money,
        available_money=available_money,
        purchase_requests_total_allocated=purchase_requests_total,
        available_after_purchase_requests=available_money - purchase_requests_total,
        public_purchase_plan_list_id=budget.public_purchase_plan_list_id,
        public_purchase_plan_list=_plan_list_out(plan_list, session) if plan_list else None,
        fundings=[_funding_out(funding) for funding in fundings],
        purchase_requests=[
            PurchaseRequestForBudgetOut(
                purchase_request_id=purchase_request.purchase_request_id,
                purchase_request_name=purchase_request.purchase_request_name,
                budget_allocated_for_the_order=purchase_request.budget_allocated_for_the_order,
                if_service=purchase_request.if_service,
                used_cpv_id=purchase_request.used_cpv_id,
                created_at=purchase_request.created_at.isoformat() if purchase_request.created_at else None,
                can_add=purchase_request.can_add,
                project_finance_manager_id=purchase_request.project_finance_manager_id,
                project_budget_id=purchase_request.project_budget_id,
            )
            for purchase_request in purchase_requests
        ],
    )


def _get_budget_for_plan_list(
    public_purchase_plan_list_id: int,
    session: Session,
) -> AssociationBudget:
    budget = session.exec(
        select(AssociationBudget).where(
            AssociationBudget.public_purchase_plan_list_id == public_purchase_plan_list_id
        )
    ).first()
    if not budget:
        raise HTTPException(
            status_code=400,
            detail="Lista planów publicznych nie jest przypięta do budżetu koła",
        )
    return budget


def _validate_funding_for_budget(
    funding_id: int,
    association_budget_id: int,
    session: Session,
) -> Funding:
    funding = session.get(Funding, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Dofinansowanie nie znalezione")
    if funding.association_budget_id != association_budget_id:
        raise HTTPException(
            status_code=400,
            detail="Dofinansowanie nie należy do wskazanego budżetu koła",
        )
    return funding


@app.get("/api/association_budgets", response_model=List[AssociationBudgetOut])
def get_association_budgets(
    association_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    statement = select(AssociationBudget)
    if association_id:
        statement = (
            statement
            .join(ProjectBudget)
            .join(Project)
            .where(Project.association_id == association_id)
            .distinct()
        )

    budgets = session.exec(statement).all()
    return [_budget_out(budget, session, association_id) for budget in budgets]


@app.get("/api/project_budgets", response_model=List[ProjectBudgetOut])
def get_project_budgets(
    association_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    statement = select(ProjectBudget)
    if association_id:
        statement = (
            statement
            .join(Project)
            .where(Project.association_id == association_id)
        )
    project_budgets = session.exec(
        statement.order_by(ProjectBudget.project_budget_id)
    ).all()

    result = []
    for project_budget in project_budgets:
        requests = session.exec(
            select(PurchaseRequest).where(
                PurchaseRequest.project_budget_id == project_budget.project_budget_id
            )
        ).all()
        allocated = sum(request.budget_allocated_for_the_order for request in requests)
        association_budget = session.get(
            AssociationBudget, project_budget.association_budget_id
        )
        project = session.get(Project, project_budget.project_id)
        result.append(ProjectBudgetOut(
            project_budget_id=project_budget.project_budget_id,
            project_budget_name=project_budget.project_budget_name,
            total_budget=project_budget.total_budget,
            spent_money=project_budget.spent_money,
            purchase_requests_total_allocated=allocated,
            available_after_purchase_requests=(
                project_budget.total_budget - project_budget.spent_money - allocated
            ),
            association_budget_id=project_budget.association_budget_id,
            association_budget_name=(
                association_budget.association_budget_name if association_budget else None
            ),
            project_id=project_budget.project_id,
            project_name=project.project_name if project else None,
        ))
    return result


@app.get("/api/dashboard/budget_summary", response_model=DashboardBudgetSummaryOut)
def get_dashboard_budget_summary(
    association_id: int,
    session: Session = Depends(get_session),
):
    project_budgets = session.exec(
        select(ProjectBudget)
        .join(Project)
        .where(Project.association_id == association_id)
    ).all()
    association_budget_ids = {
        project_budget.association_budget_id for project_budget in project_budgets
    }
    association_budgets = [
        session.get(AssociationBudget, budget_id)
        for budget_id in association_budget_ids
    ]
    association_budgets = [budget for budget in association_budgets if budget]
    project_budget_ids = [
        project_budget.project_budget_id for project_budget in project_budgets
    ]
    requests = (
        session.exec(
            select(PurchaseRequest).where(
                PurchaseRequest.project_budget_id.in_(project_budget_ids)
            )
        ).all()
        if project_budget_ids
        else []
    )

    total_budget = sum(budget.total_budget for budget in association_budgets)
    spent_money = sum(budget.spent_money for budget in association_budgets)
    allocated = sum(request.budget_allocated_for_the_order for request in requests)
    return DashboardBudgetSummaryOut(
        total_budget=total_budget,
        spent_money=spent_money,
        purchase_requests_total_allocated=allocated,
        available_after_purchase_requests=total_budget - spent_money - allocated,
    )


@app.post("/api/public_purchase_plan_lists", response_model=PublicPurchasePlanListOut)
def create_or_attach_public_purchase_plan_list(
    new_list_data: PublicPurchasePlanListCreate,
    session: Session = Depends(get_session),
):
    budget = session.get(AssociationBudget, new_list_data.association_budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budżet koła nie znaleziony")

    if budget.public_purchase_plan_list_id:
        plan_list = session.get(PublicPurchasePlanList, budget.public_purchase_plan_list_id)
        if not plan_list:
            raise HTTPException(status_code=404, detail="Lista planów publicznych nie znaleziona")
        plan_list.public_plan_list_name = new_list_data.public_plan_list_name
    else:
        plan_list = PublicPurchasePlanList(
            public_plan_list_name=new_list_data.public_plan_list_name
        )
        session.add(plan_list)
        session.commit()
        session.refresh(plan_list)

        budget.public_purchase_plan_list_id = plan_list.public_purchase_plan_list_id

    session.add(budget)
    session.add(plan_list)
    session.commit()
    session.refresh(plan_list)

    return _plan_list_out(plan_list, session)


@app.get(
    "/api/public_purchase_plan_lists/{public_purchase_plan_list_id}",
    response_model=PublicPurchasePlanListOut,
)
def get_public_purchase_plan_list(
    public_purchase_plan_list_id: int,
    session: Session = Depends(get_session),
):
    plan_list = session.get(PublicPurchasePlanList, public_purchase_plan_list_id)
    if not plan_list:
        raise HTTPException(status_code=404, detail="Lista planów publicznych nie znaleziona")

    return _plan_list_out(plan_list, session)


@app.post("/api/public_purchase_plans", response_model=PublicPurchasePlanOut)
def create_public_purchase_plan(
    new_plan_data: PublicPurchasePlanCreate,
    session: Session = Depends(get_session),
):
    if new_plan_data.cost <= 0:
        raise HTTPException(status_code=400, detail="Koszt planu musi być większy od zera")

    plan_list = session.get(PublicPurchasePlanList, new_plan_data.public_purchase_plan_list_id)
    if not plan_list:
        raise HTTPException(status_code=404, detail="Lista planów publicznych nie znaleziona")

    budget = _get_budget_for_plan_list(new_plan_data.public_purchase_plan_list_id, session)
    funding = _validate_funding_for_budget(
        new_plan_data.funding_id,
        budget.association_budget_id,
        session,
    )

    new_plan = PublicPurchasePlan(
        public_purchase_plan_name=new_plan_data.public_purchase_plan_name,
        cost=new_plan_data.cost,
        funding_id=new_plan_data.funding_id,
        public_purchase_plan_list_id=new_plan_data.public_purchase_plan_list_id,
    )
    session.add(new_plan)
    session.commit()
    session.refresh(new_plan)

    return PublicPurchasePlanOut(
        public_purchase_plan_id=new_plan.public_purchase_plan_id,
        public_purchase_plan_name=new_plan.public_purchase_plan_name,
        cost=new_plan.cost,
        funding_id=new_plan.funding_id,
        funding_name=funding.funding_name,
        public_purchase_plan_list_id=new_plan.public_purchase_plan_list_id,
    )


@app.delete("/api/public_purchase_plans/{public_purchase_plan_id}")
def delete_public_purchase_plan(
    public_purchase_plan_id: int,
    session: Session = Depends(get_session),
):
    plan = session.get(PublicPurchasePlan, public_purchase_plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan publiczny nie znaleziony")

    session.delete(plan)
    session.commit()
    return {"status": "success"}
