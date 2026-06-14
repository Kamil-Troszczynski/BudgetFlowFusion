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
    project_budget_id: Optional[int] = None
    funding_id: Optional[int] = None
    created_at: datetime
    created_by_user_id: Optional[int] = None
    can_add: bool = True
    project_finance_manager_id: int
    shop_purchase_list_id: Optional[int] = None
    public_purchase_plan_id: Optional[int] = None
    plan_exception_justification: Optional[str] = None


class PurchaseRequestBudgetOut(BaseModel):
    project_budget_id: int
    project_budget_name: str
    project_total_budget: float
    project_spent_money: float
    project_purchase_requests_total_allocated: float
    project_available_after_purchase_requests: float
    funding_id: int
    funding_name: str
    funding_total: float
    funding_spent_money: float
    funding_purchase_requests_total_allocated: float
    funding_available_after_purchase_requests: float
    association_budget_id: int
    association_budget_name: str
    total_budget: float
    spent_money: float
    available_money: float
    purchase_requests_total_allocated: float
    available_after_purchase_requests: float


class SourceShopPurchaseListOut(BaseModel):
    shop_purchase_list_id: int
    name: Optional[str] = None
    shop_name: Optional[str] = None
    total_price: Optional[float] = None
    settlement_id: Optional[int] = None
    funding_id: Optional[int] = None
    funding_name: Optional[str] = None


class PurchasePlanPositionOut(BaseModel):
    public_purchase_plan_id: int
    cpv_code: int
    planned_amount: float
    used_amount: float
    remaining_amount: float
    plan_year: int


class PurchaseRequestOut(BaseModel):
    purchase_request_id: int
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[int] = None
    project_budget_id: int
    project_budget_name: Optional[str] = None
    funding_id: int
    funding_name: Optional[str] = None
    association_budget_id: int
    association_budget_name: Optional[str] = None
    created_at: datetime
    can_add: bool
    gslbccf_id: Optional[int] = None
    project_finance_manager_id: Optional[int] = None
    public_purchase_plan_id: Optional[int] = None
    plan_position: Optional[PurchasePlanPositionOut] = None
    plan_exception_justification: Optional[str] = None
    plan_compliance_status: str
    budget_info: Optional[PurchaseRequestBudgetOut] = None
    source_shop_purchase_list: Optional[SourceShopPurchaseListOut] = None


def _shop_purchase_list_total(shop_purchase_list: ShopPurchaseList, session: Session) -> float:
    line_items = session.exec(
        select(ShopPurchaseListItem).where(
            ShopPurchaseListItem.shop_purchase_list_id == shop_purchase_list.shop_purchase_list_id
        )
    ).all()
    total = 0.0
    for line in line_items:
        item = session.get(Item, line.item_id)
        if item:
            total += (item.price or 0) * line.amount
    return total or shop_purchase_list.cost or 0.0


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


def _source_list_for_request(request: PurchaseRequest, session: Session) -> Optional[SourceShopPurchaseListOut]:
    settlement = session.exec(
        select(Settlement).where(Settlement.purchase_request_id == request.purchase_request_id)
    ).first()
    if not settlement:
        return None

    purchase_list = session.exec(
        select(ShopPurchaseList).where(ShopPurchaseList.settlement_id == settlement.settlement_id)
    ).first()
    if not purchase_list:
        return None

    shop = session.get(Shop, purchase_list.shop_id)
    funding = session.get(Funding, purchase_list.funding_id)
    return SourceShopPurchaseListOut(
        shop_purchase_list_id=purchase_list.shop_purchase_list_id,
        name=purchase_list.name,
        shop_name=shop.shop_name if shop else None,
        total_price=_shop_purchase_list_total(purchase_list, session),
        settlement_id=settlement.settlement_id,
        funding_id=funding.funding_id if funding else None,
        funding_name=funding.funding_name if funding else None,
    )


def _budget_info_for_request(request: PurchaseRequest, session: Session) -> Optional[PurchaseRequestBudgetOut]:
    project_budget = session.get(ProjectBudget, request.project_budget_id)
    if not project_budget:
        return None
    budget = session.get(AssociationBudget, project_budget.association_budget_id)
    if not budget:
        return None
    funding = session.get(Funding, request.funding_id)
    if not funding:
        return None

    project_purchase_requests = session.exec(
        select(PurchaseRequest).where(
            PurchaseRequest.project_budget_id == project_budget.project_budget_id
        )
    ).all()
    project_total_allocated = sum(
        purchase_request.budget_allocated_for_the_order
        for purchase_request in project_purchase_requests
    )
    association_purchase_requests = session.exec(
        select(PurchaseRequest)
        .join(ProjectBudget)
        .where(ProjectBudget.association_budget_id == budget.association_budget_id)
    ).all()
    association_total_allocated = sum(
        purchase_request.budget_allocated_for_the_order
        for purchase_request in association_purchase_requests
    )
    funding_purchase_requests = session.exec(
        select(PurchaseRequest).where(PurchaseRequest.funding_id == funding.funding_id)
    ).all()
    funding_total_allocated = sum(
        purchase_request.budget_allocated_for_the_order
        for purchase_request in funding_purchase_requests
    )

    project_total_budget, project_spent_money = _project_budget_amounts(
        project_budget, session
    )
    association_project_budgets = session.exec(
        select(ProjectBudget).where(
            ProjectBudget.association_budget_id == budget.association_budget_id
        )
    ).all()
    association_amounts = [
        _project_budget_amounts(item, session) for item in association_project_budgets
    ]
    association_total_budget = sum(total for total, _ in association_amounts)
    association_spent_money = sum(spent for _, spent in association_amounts)
    available_money = association_total_budget - association_spent_money
    return PurchaseRequestBudgetOut(
        project_budget_id=project_budget.project_budget_id,
        project_budget_name=project_budget.project_budget_name,
        project_total_budget=project_total_budget,
        project_spent_money=project_spent_money,
        project_purchase_requests_total_allocated=project_total_allocated,
        project_available_after_purchase_requests=(
            project_total_budget
            - project_spent_money
            - project_total_allocated
        ),
        funding_id=funding.funding_id,
        funding_name=funding.funding_name,
        funding_total=funding.funding_price,
        funding_spent_money=funding.spent_money,
        funding_purchase_requests_total_allocated=funding_total_allocated,
        funding_available_after_purchase_requests=(
            funding.funding_price - funding.spent_money - funding_total_allocated
        ),
        association_budget_id=budget.association_budget_id,
        association_budget_name=budget.association_budget_name,
        total_budget=association_total_budget,
        spent_money=association_spent_money,
        available_money=available_money,
        purchase_requests_total_allocated=association_total_allocated,
        available_after_purchase_requests=available_money - association_total_allocated,
    )


def _purchase_request_out(request: PurchaseRequest, session: Session) -> PurchaseRequestOut:
    budget_info = _budget_info_for_request(request, session)
    plan_position = None
    if request.public_purchase_plan_id:
        plan = session.get(PublicPurchasePlan, request.public_purchase_plan_id)
        if plan:
            plan_list = session.get(
                PublicPurchasePlanList, plan.public_purchase_plan_list_id
            )
            linked_requests = session.exec(
                select(PurchaseRequest).where(
                    PurchaseRequest.public_purchase_plan_id
                    == plan.public_purchase_plan_id
                )
            ).all()
            used_amount = sum(
                linked_request.budget_allocated_for_the_order
                for linked_request in linked_requests
            )
            plan_position = PurchasePlanPositionOut(
                public_purchase_plan_id=plan.public_purchase_plan_id,
                cpv_code=plan.cpv_code,
                planned_amount=plan.cost,
                used_amount=used_amount,
                remaining_amount=plan.cost - used_amount,
                plan_year=plan_list.plan_year if plan_list else 0,
            )

    return PurchaseRequestOut(
        purchase_request_id=request.purchase_request_id,
        purchase_request_name=request.purchase_request_name,
        budget_allocated_for_the_order=request.budget_allocated_for_the_order,
        if_service=request.if_service,
        used_cpv_id=request.used_cpv_id,
        project_budget_id=request.project_budget_id,
        project_budget_name=budget_info.project_budget_name if budget_info else None,
        funding_id=request.funding_id,
        funding_name=budget_info.funding_name if budget_info else None,
        association_budget_id=budget_info.association_budget_id if budget_info else 0,
        association_budget_name=budget_info.association_budget_name if budget_info else None,
        created_at=request.created_at,
        can_add=request.can_add,
        gslbccf_id=request.gslbccf_id,
        project_finance_manager_id=request.project_finance_manager_id,
        public_purchase_plan_id=request.public_purchase_plan_id,
        plan_position=plan_position,
        plan_exception_justification=request.plan_exception_justification,
        plan_compliance_status=request.plan_compliance_status,
        budget_info=budget_info,
        source_shop_purchase_list=_source_list_for_request(request, session),
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
    source_list = None
    source_settlement = None
    source_gslbccf_id = None
    budget_allocated = new_purchase_request_data.budget_allocated_for_the_order
    project_budget_id = new_purchase_request_data.project_budget_id
    funding_id = new_purchase_request_data.funding_id

    if new_purchase_request_data.shop_purchase_list_id:
        source_list = session.get(ShopPurchaseList, new_purchase_request_data.shop_purchase_list_id)
        if not source_list:
            raise HTTPException(status_code=404, detail="Zamknięte zamówienie nie znalezione")

        source_student = session.get(Student, source_list.student_id)
        if (
            not source_student
            or source_student.project_finance_manager_id != new_purchase_request_data.project_finance_manager_id
        ):
            raise HTTPException(status_code=403, detail="Możesz utworzyć wniosek tylko ze swojego zamkniętego zamówienia")

        if source_list.settlement_id is None:
            raise HTTPException(status_code=400, detail="Wniosek można utworzyć tylko z zamkniętego zamówienia")

        source_settlement = session.get(Settlement, source_list.settlement_id)
        if not source_settlement:
            raise HTTPException(status_code=400, detail="Zamknięte zamówienie nie ma rozliczenia")
        if source_settlement.purchase_request_id is not None:
            raise HTTPException(status_code=400, detail="To zamówienie ma już utworzony wniosek")

        source_funding = session.get(Funding, source_list.funding_id)
        if not source_funding:
            raise HTTPException(status_code=404, detail="Dofinansowanie zamówienia nie znalezione")

        project_budget_id = source_funding.project_budget_id
        funding_id = source_funding.funding_id
        budget_allocated = _shop_purchase_list_total(source_list, session)
        source_gslbccf_id = source_list.gslbccf_id

    if not project_budget_id:
        raise HTTPException(status_code=400, detail="Budżet sekcji jest wymagany")

    project_budget = session.get(ProjectBudget, project_budget_id)
    if not project_budget:
        raise HTTPException(status_code=404, detail="Budżet sekcji nie znaleziony")

    if not funding_id:
        raise HTTPException(status_code=400, detail="Dofinansowanie jest wymagane")
    funding = session.get(Funding, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Dofinansowanie nie znalezione")
    if funding.project_budget_id != project_budget.project_budget_id:
        raise HTTPException(
            status_code=400,
            detail="Dofinansowanie nie należy do wskazanej sekcji",
        )

    project = session.get(Project, project_budget.project_id)
    source_student = session.get(Student, source_list.student_id) if source_list else None
    if source_student and (
        not project or project.association_id != source_student.association_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Wybrany budżet sekcji nie należy do koła skarbnika",
        )

    allocated_in_requests = sum(
        request.budget_allocated_for_the_order
        for request in session.exec(
            select(PurchaseRequest).where(
                PurchaseRequest.project_budget_id == project_budget.project_budget_id
            )
        ).all()
    )
    project_total_budget, project_spent_money = _project_budget_amounts(
        project_budget, session
    )
    available_project_budget = project_total_budget - project_spent_money - allocated_in_requests
    allocated_from_funding = sum(
        request.budget_allocated_for_the_order
        for request in session.exec(
            select(PurchaseRequest).where(PurchaseRequest.funding_id == funding.funding_id)
        ).all()
    )
    available_funding = funding.funding_price - funding.spent_money - allocated_from_funding
    if budget_allocated <= 0:
        raise HTTPException(status_code=400, detail="Kwota wniosku musi być większa od zera")
    if budget_allocated > available_project_budget:
        raise HTTPException(
            status_code=400,
            detail="Kwota wniosku przekracza dostępny budżet sekcji",
        )
    if budget_allocated > available_funding:
        raise HTTPException(
            status_code=400,
            detail="Kwota wniosku przekracza dostępne środki dofinansowania",
        )
    if not new_purchase_request_data.used_cpv_id or new_purchase_request_data.used_cpv_id <= 0:
        raise HTTPException(status_code=400, detail="Kod CPV jest wymagany")

    plan = None
    plan_compliance_status = "compliant"
    justification = (
        new_purchase_request_data.plan_exception_justification or ""
    ).strip()
    if new_purchase_request_data.public_purchase_plan_id:
        plan = session.get(
            PublicPurchasePlan,
            new_purchase_request_data.public_purchase_plan_id,
        )
        if not plan:
            raise HTTPException(
                status_code=404, detail="Pozycja planu zamówień nie znaleziona"
            )
        if plan.funding_id != funding.funding_id:
            raise HTTPException(
                status_code=400,
                detail="Pozycja planu nie należy do dofinansowania zamówienia",
            )
        if plan.cpv_code != new_purchase_request_data.used_cpv_id:
            raise HTTPException(
                status_code=400,
                detail="Kod CPV wniosku nie zgadza się z pozycją planu",
            )
        used_from_plan = sum(
            request.budget_allocated_for_the_order
            for request in session.exec(
                select(PurchaseRequest).where(
                    PurchaseRequest.public_purchase_plan_id
                    == plan.public_purchase_plan_id
                )
            ).all()
        )
        if budget_allocated > plan.cost - used_from_plan:
            plan_compliance_status = "requires_approval"
    else:
        plan_compliance_status = "requires_approval"

    if plan_compliance_status == "requires_approval" and not justification:
        raise HTTPException(
            status_code=400,
            detail=(
                "Brak pozycji w planie lub przekroczona kwota planu. "
                "Uzasadnienie odstępstwa jest wymagane"
            ),
        )

    new_purchase_request = PurchaseRequest(
        purchase_request_name = new_purchase_request_data.purchase_request_name,
        budget_allocated_for_the_order = budget_allocated,
        if_service = new_purchase_request_data.if_service,
        used_cpv_id = new_purchase_request_data.used_cpv_id,
        project_budget_id = project_budget.project_budget_id,
        funding_id = funding.funding_id,
        created_at = new_purchase_request_data.created_at,
        can_add = new_purchase_request_data.can_add,
        project_finance_manager_id = new_purchase_request_data.project_finance_manager_id,
        gslbccf_id = source_gslbccf_id,
        public_purchase_plan_id = plan.public_purchase_plan_id if plan else None,
        plan_exception_justification = justification or None,
        plan_compliance_status = plan_compliance_status,
    )
    if source_settlement:
        session.add(source_settlement)

    session.add(new_purchase_request)
    session.flush()
    if source_settlement:
        source_settlement.purchase_request_id = new_purchase_request.purchase_request_id
    session.commit()
    session.refresh(new_purchase_request)

    return _purchase_request_out(new_purchase_request, session)


@app.delete("/api/purchase_requests/{purchase_request_id}")
def delete_purchase_request(purchase_request_id: int, session: Session = Depends(get_session)):
    purchase_request = session.exec(select(PurchaseRequest).where(PurchaseRequest.purchase_request_id == purchase_request_id)).first()
    if not purchase_request:
        raise HTTPException(status_code = 404, detail = "Wniosek nie znaleziony")
    settlements = session.exec(
        select(Settlement).where(Settlement.purchase_request_id == purchase_request_id)
    ).all()
    for settlement in settlements:
        settlement.purchase_request_id = None
        session.add(settlement)
    session.delete(purchase_request)
    session.commit()
    return {"message": "Wniosek usunięty pomyślnie"}
