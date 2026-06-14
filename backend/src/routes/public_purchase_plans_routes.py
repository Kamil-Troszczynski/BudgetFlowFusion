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
    purchase_requests_total_allocated: float = 0.0
    available_after_purchase_requests: float = 0.0
    project_id: Optional[int] = None
    project_budget_id: int
    project_budget_name: Optional[str] = None


class PublicPurchasePlanOut(BaseModel):
    public_purchase_plan_id: int
    cpv_code: int
    cost: float
    used_amount: float = 0.0
    remaining_amount: float = 0.0
    funding_id: int
    public_purchase_plan_list_id: int


class PublicPurchasePlanListOut(BaseModel):
    public_purchase_plan_list_id: int
    public_plan_list_name: str
    plan_year: int
    funding_id: int
    funding_name: str
    funding_price: float
    public_purchase_plans: List[PublicPurchasePlanOut] = PydanticField(default_factory=list)
    total_cost: float = 0.0
    total_used: float = 0.0
    total_remaining: float = 0.0


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
    funding_id: int
    public_plan_list_name: str
    plan_year: int


class PublicPurchasePlanCreate(BaseModel):
    public_purchase_plan_list_id: int
    cpv_code: int
    cost: float


def _funding_out(funding: Funding, session: Session) -> FundingOut:
    project_budget = session.get(ProjectBudget, funding.project_budget_id)
    purchase_requests = session.exec(
        select(PurchaseRequest).where(PurchaseRequest.funding_id == funding.funding_id)
    ).all()
    allocated = sum(
        request.budget_allocated_for_the_order for request in purchase_requests
    )
    return FundingOut(
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
    )


def _plan_list_out(plan_list: PublicPurchasePlanList, session: Session) -> PublicPurchasePlanListOut:
    funding = session.get(Funding, plan_list.funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Dofinansowanie planu nie znalezione")

    plans = session.exec(
        select(PublicPurchasePlan)
        .where(PublicPurchasePlan.public_purchase_plan_list_id == plan_list.public_purchase_plan_list_id)
        .order_by(PublicPurchasePlan.cpv_code)
    ).all()
    public_plans = []
    for plan in plans:
        requests = session.exec(
            select(PurchaseRequest).where(
                PurchaseRequest.public_purchase_plan_id == plan.public_purchase_plan_id
            )
        ).all()
        used_amount = sum(
            request.budget_allocated_for_the_order for request in requests
        )
        public_plans.append(PublicPurchasePlanOut(
            public_purchase_plan_id=plan.public_purchase_plan_id,
            cpv_code=plan.cpv_code,
            cost=plan.cost,
            used_amount=used_amount,
            remaining_amount=plan.cost - used_amount,
            funding_id=plan_list.funding_id,
            public_purchase_plan_list_id=plan.public_purchase_plan_list_id,
        ))

    return PublicPurchasePlanListOut(
        public_purchase_plan_list_id=plan_list.public_purchase_plan_list_id,
        public_plan_list_name=plan_list.public_plan_list_name,
        plan_year=plan_list.plan_year,
        funding_id=plan_list.funding_id,
        funding_name=funding.funding_name,
        funding_price=funding.funding_price,
        public_purchase_plans=public_plans,
        total_cost=sum(plan.cost for plan in plans),
        total_used=sum(plan.used_amount for plan in public_plans),
        total_remaining=sum(plan.remaining_amount for plan in public_plans),
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


def _project_budget_amounts(project_budget: ProjectBudget, session: Session) -> tuple[float, float]:
    fundings = session.exec(
        select(Funding).where(
            Funding.project_budget_id == project_budget.project_budget_id
        )
    ).all()
    if not fundings:
        return project_budget.total_budget, project_budget.spent_money
    return (
        sum(funding.funding_price for funding in fundings),
        sum(funding.spent_money for funding in fundings),
    )


def _association_budget_amounts(budget_id: int, session: Session) -> tuple[float, float]:
    project_budgets = session.exec(
        select(ProjectBudget).where(ProjectBudget.association_budget_id == budget_id)
    ).all()
    amounts = [_project_budget_amounts(project_budget, session) for project_budget in project_budgets]
    return (
        sum(total for total, _ in amounts),
        sum(spent for _, spent in amounts),
    )


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
    total_budget, spent_money = _association_budget_amounts(
        budget.association_budget_id, session
    )
    available_money = total_budget - spent_money
    return AssociationBudgetOut(
        association_budget_id=budget.association_budget_id,
        association_budget_name=budget.association_budget_name,
        total_budget=total_budget,
        spent_money=spent_money,
        available_money=available_money,
        purchase_requests_total_allocated=purchase_requests_total,
        available_after_purchase_requests=available_money - purchase_requests_total,
        public_purchase_plan_list_id=budget.public_purchase_plan_list_id,
        public_purchase_plan_list=None,
        fundings=[_funding_out(funding, session) for funding in fundings],
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
        total_budget, spent_money = _project_budget_amounts(project_budget, session)
        result.append(ProjectBudgetOut(
            project_budget_id=project_budget.project_budget_id,
            project_budget_name=project_budget.project_budget_name,
            total_budget=total_budget,
            spent_money=spent_money,
            purchase_requests_total_allocated=allocated,
            available_after_purchase_requests=(
                total_budget - spent_money - allocated
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

    budget_amounts = [
        _project_budget_amounts(project_budget, session)
        for project_budget in project_budgets
    ]
    total_budget = sum(total for total, _ in budget_amounts)
    spent_money = sum(spent for _, spent in budget_amounts)
    allocated = sum(request.budget_allocated_for_the_order for request in requests)
    return DashboardBudgetSummaryOut(
        total_budget=total_budget,
        spent_money=spent_money,
        purchase_requests_total_allocated=allocated,
        available_after_purchase_requests=total_budget - spent_money - allocated,
    )


@app.post("/api/public_purchase_plan_lists", response_model=PublicPurchasePlanListOut)
def create_public_purchase_plan_list(
    new_list_data: PublicPurchasePlanListCreate,
    session: Session = Depends(get_session),
):
    funding = session.get(Funding, new_list_data.funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Dofinansowanie nie znalezione")
    if new_list_data.plan_year < 2000 or new_list_data.plan_year > 2100:
        raise HTTPException(status_code=400, detail="Nieprawidłowy rok planu")

    plan_list = session.exec(
        select(PublicPurchasePlanList).where(
            PublicPurchasePlanList.funding_id == funding.funding_id
        )
    ).first()
    if plan_list:
        plan_list.public_plan_list_name = new_list_data.public_plan_list_name
        plan_list.plan_year = new_list_data.plan_year
    else:
        plan_list = PublicPurchasePlanList(
            public_plan_list_name=new_list_data.public_plan_list_name,
            plan_year=new_list_data.plan_year,
            funding_id=funding.funding_id,
        )

    session.add(plan_list)
    session.commit()
    session.refresh(plan_list)

    return _plan_list_out(plan_list, session)


@app.get("/api/public_purchase_plan_lists", response_model=List[PublicPurchasePlanListOut])
def get_public_purchase_plan_lists(
    association_id: Optional[int] = None,
    funding_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    statement = select(PublicPurchasePlanList)
    if funding_id:
        statement = statement.where(PublicPurchasePlanList.funding_id == funding_id)
    if association_id:
        statement = (
            statement.join(Funding)
            .join(Project)
            .where(Project.association_id == association_id)
        )
    plan_lists = session.exec(
        statement.order_by(PublicPurchasePlanList.plan_year.desc())
    ).all()
    return [_plan_list_out(plan_list, session) for plan_list in plan_lists]


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
        raise HTTPException(status_code=400, detail="Kwota planowana musi być większa od zera")
    if new_plan_data.cpv_code <= 0:
        raise HTTPException(status_code=400, detail="Kod CPV jest wymagany")

    plan_list = session.get(PublicPurchasePlanList, new_plan_data.public_purchase_plan_list_id)
    if not plan_list:
        raise HTTPException(status_code=404, detail="Lista planów publicznych nie znaleziona")

    duplicate = session.exec(
        select(PublicPurchasePlan).where(
            PublicPurchasePlan.public_purchase_plan_list_id
            == plan_list.public_purchase_plan_list_id,
            PublicPurchasePlan.cpv_code == new_plan_data.cpv_code,
        )
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Ten kod CPV już istnieje w planie dofinansowania",
        )

    new_plan = PublicPurchasePlan(
        public_purchase_plan_name=f"CPV {new_plan_data.cpv_code}",
        cpv_code=new_plan_data.cpv_code,
        cost=new_plan_data.cost,
        funding_id=plan_list.funding_id,
        public_purchase_plan_list_id=new_plan_data.public_purchase_plan_list_id,
    )
    session.add(new_plan)
    session.commit()
    session.refresh(new_plan)

    return PublicPurchasePlanOut(
        public_purchase_plan_id=new_plan.public_purchase_plan_id,
        cpv_code=new_plan.cpv_code,
        cost=new_plan.cost,
        used_amount=0.0,
        remaining_amount=new_plan.cost,
        funding_id=new_plan.funding_id,
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
    linked_request = session.exec(
        select(PurchaseRequest).where(
            PurchaseRequest.public_purchase_plan_id == public_purchase_plan_id
        )
    ).first()
    if linked_request:
        raise HTTPException(
            status_code=400,
            detail="Nie można usunąć pozycji planu użytej we wniosku",
        )

    session.delete(plan)
    session.commit()
    return {"status": "success"}
