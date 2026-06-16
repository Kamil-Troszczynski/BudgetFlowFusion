from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field as PydanticField
from datetime import datetime



class PurchaseRequestFundingAllocationIn(BaseModel):
    funding_id: int
    allocated_amount: float


class PurchaseRequestCreate(BaseModel):
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[int]
    section_name: Optional[str] = None
    project_budget_id: Optional[int] = None
    funding_id: Optional[int] = None
    created_at: datetime
    created_by_user_id: Optional[int] = None
    can_add: bool = True
    project_finance_manager_id: int
    shop_purchase_list_id: Optional[int] = None
    public_purchase_plan_id: Optional[int] = None
    plan_exception_justification: Optional[str] = None
    funding_allocations: List[PurchaseRequestFundingAllocationIn] = PydanticField(default_factory=list)


class PurchaseRequestUpdate(BaseModel):
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[int]
    can_add: bool = True
    public_purchase_plan_id: Optional[int] = None
    plan_exception_justification: Optional[str] = None
    funding_allocations: List[PurchaseRequestFundingAllocationIn] = PydanticField(default_factory=list)


class PurchaseRequestFundingAllocationOut(BaseModel):
    funding_id: int
    funding_name: Optional[str] = None
    project_budget_id: Optional[int] = None
    project_budget_name: Optional[str] = None
    allocated_amount: float


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
    total_net: Optional[float] = None
    shop_count: int = 0
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
    funding_allocations: List[PurchaseRequestFundingAllocationOut] = PydanticField(default_factory=list)


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


def _ensure_group_for_plan(plan: PublicPurchasePlan, session: Session) -> int:
    if plan.gslbccf_id:
        return plan.gslbccf_id

    grouped_shops_list = GroupedShopsListByCpvCategoryAndFunding(
        allocated_money=plan.cost
    )
    session.add(grouped_shops_list)
    session.commit()
    session.refresh(grouped_shops_list)

    plan.gslbccf_id = grouped_shops_list.gslbccf_id
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan.gslbccf_id


def _default_budget_and_funding_for_manager(
    project_finance_manager_id: int,
    session: Session,
    section_name: Optional[str] = None,
) -> tuple[Optional[ProjectBudget], Optional[Funding]]:
    manager_student = session.exec(
        select(Student).where(
            Student.project_finance_manager_id == project_finance_manager_id
        )
    ).first()
    if not manager_student or not manager_student.association_id:
        return None, None

    statement = (
        select(Funding, ProjectBudget)
        .join(ProjectBudget, Funding.project_budget_id == ProjectBudget.project_budget_id)
        .join(Project, ProjectBudget.project_id == Project.project_id)
        .where(Project.association_id == manager_student.association_id)
    )
    if section_name:
        statement = statement.where(ProjectBudget.project_budget_name == section_name)

    result = session.exec(statement).first()
    if not result:
        return None, None
    funding, project_budget = result
    return project_budget, funding


def _allocations_for_request(
    purchase_request_id: int,
    session: Session,
) -> List[PurchaseRequestFundingAllocationOut]:
    allocations = session.exec(
        select(PurchaseRequestFundingAllocation).where(
            PurchaseRequestFundingAllocation.purchase_request_id == purchase_request_id
        )
    ).all()
    result = []
    for allocation in allocations:
        funding = session.get(Funding, allocation.funding_id)
        project_budget = session.get(ProjectBudget, funding.project_budget_id) if funding else None
        result.append(PurchaseRequestFundingAllocationOut(
            funding_id=allocation.funding_id,
            funding_name=funding.funding_name if funding else None,
            project_budget_id=project_budget.project_budget_id if project_budget else None,
            project_budget_name=project_budget.project_budget_name if project_budget else None,
            allocated_amount=allocation.allocated_amount,
        ))
    return result


def _replace_request_allocations(
    purchase_request_id: int,
    allocations_data: List[PurchaseRequestFundingAllocationIn],
    session: Session,
):
    existing = session.exec(
        select(PurchaseRequestFundingAllocation).where(
            PurchaseRequestFundingAllocation.purchase_request_id == purchase_request_id
        )
    ).all()
    for allocation in existing:
        session.delete(allocation)

    merged: dict[int, float] = {}
    for allocation in allocations_data:
        amount = float(allocation.allocated_amount or 0)
        if amount <= 0:
            continue
        merged[allocation.funding_id] = merged.get(allocation.funding_id, 0.0) + amount

    for funding_id, amount in merged.items():
        session.add(PurchaseRequestFundingAllocation(
            purchase_request_id=purchase_request_id,
            funding_id=funding_id,
            allocated_amount=amount,
        ))


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
    if request.gslbccf_id:
        purchase_lists = session.exec(
            select(ShopPurchaseList).where(
                ShopPurchaseList.gslbccf_id == request.gslbccf_id
            )
        ).all()
        if purchase_lists:
            total_price = 0.0
            for purchase_list in purchase_lists:
                total_price += _shop_purchase_list_total(purchase_list, session)
            first_list = purchase_lists[0]
            first_shop = session.get(Shop, first_list.shop_id)
            first_funding = session.get(Funding, first_list.funding_id)
            return SourceShopPurchaseListOut(
                shop_purchase_list_id=first_list.shop_purchase_list_id,
                name=(
                    first_list.name
                    if len(purchase_lists) == 1
                    else f"Koszyki sklepowe ({len(purchase_lists)})"
                ),
                shop_name=(
                    first_shop.shop_name
                    if len(purchase_lists) == 1 and first_shop
                    else f"{len(purchase_lists)} sklepy"
                ),
                total_price=total_price,
                total_net=total_price / 1.23 if total_price else 0.0,
                shop_count=len(purchase_lists),
                settlement_id=first_list.settlement_id,
                funding_id=first_funding.funding_id if first_funding else None,
                funding_name=first_funding.funding_name if first_funding else None,
            )

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
        total_net=_shop_purchase_list_total(purchase_list, session) / 1.23,
        shop_count=1,
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
        funding_allocations=_allocations_for_request(request.purchase_request_id, session),
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
def get_purchase_requests(
    association_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    statement = select(PurchaseRequest)
    if association_id:
        statement = (
            statement
            .join(ProjectBudget)
            .join(Project)
            .where(Project.association_id == association_id)
        )
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
    funding_allocations_data = new_purchase_request_data.funding_allocations or []
    if funding_allocations_data:
        budget_allocated = sum(
            float(allocation.allocated_amount or 0)
            for allocation in funding_allocations_data
        )
        funding_id = funding_allocations_data[0].funding_id
        first_funding = session.get(Funding, funding_id)
        if first_funding:
            project_budget_id = first_funding.project_budget_id

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

    if not project_budget_id or not funding_id:
        default_project_budget, default_funding = _default_budget_and_funding_for_manager(
            new_purchase_request_data.project_finance_manager_id,
            session,
            new_purchase_request_data.section_name,
        )
        if not default_project_budget or not default_funding:
            if new_purchase_request_data.section_name:
                raise HTTPException(status_code=400, detail="Nie znaleziono dofinansowania dla wybranej sekcji")
            raise HTTPException(status_code=400, detail="Brak dostepnego dofinansowania dla skarbnika")
        project_budget_id = project_budget_id or default_project_budget.project_budget_id
        funding_id = funding_id or default_funding.funding_id

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
    is_draft = budget_allocated <= 0
    if not is_draft and budget_allocated > available_project_budget:
        raise HTTPException(
            status_code=400,
            detail="Kwota wniosku przekracza dostępny budżet sekcji",
        )
    if not is_draft and budget_allocated > available_funding:
        raise HTTPException(
            status_code=400,
            detail="Kwota wniosku przekracza dostępne środki dofinansowania",
        )
    if not is_draft and (not new_purchase_request_data.used_cpv_id or new_purchase_request_data.used_cpv_id <= 0):
        raise HTTPException(status_code=400, detail="Kod CPV jest wymagany")

    plan = None
    plan_compliance_status = "draft" if is_draft else "compliant"
    justification = (
        new_purchase_request_data.plan_exception_justification or ""
    ).strip()
    if not is_draft and new_purchase_request_data.public_purchase_plan_id:
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
    elif not is_draft:
        plan_compliance_status = "requires_approval"

    if not is_draft and plan_compliance_status == "requires_approval" and not justification:
        raise HTTPException(
            status_code=400,
            detail=(
                "Brak pozycji w planie lub przekroczona kwota planu. "
                "Uzasadnienie odstępstwa jest wymagane"
            ),
        )

    if not source_gslbccf_id:
        if plan:
            source_gslbccf_id = _ensure_group_for_plan(plan, session)
        else:
            grouped_shops_list = GroupedShopsListByCpvCategoryAndFunding(
                allocated_money=budget_allocated
            )
            session.add(grouped_shops_list)
            session.commit()
            session.refresh(grouped_shops_list)
            source_gslbccf_id = grouped_shops_list.gslbccf_id

    new_purchase_request = PurchaseRequest(
        purchase_request_name = new_purchase_request_data.purchase_request_name,
        budget_allocated_for_the_order = budget_allocated,
        if_service = new_purchase_request_data.if_service,
        used_cpv_id = new_purchase_request_data.used_cpv_id or 0,
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
    if budget_allocated > 0:
        _replace_request_allocations(
            new_purchase_request.purchase_request_id,
            funding_allocations_data or [
                PurchaseRequestFundingAllocationIn(
                    funding_id=funding.funding_id,
                    allocated_amount=budget_allocated,
                )
            ],
            session,
        )
    if source_settlement:
        source_settlement.purchase_request_id = new_purchase_request.purchase_request_id
    session.commit()
    session.refresh(new_purchase_request)

    return _purchase_request_out(new_purchase_request, session)


@app.patch("/api/purchase_requests/{purchase_request_id}", response_model=PurchaseRequestOut)
def update_purchase_request(
    purchase_request_id: int,
    update_data: PurchaseRequestUpdate,
    session: Session = Depends(get_session),
):
    purchase_request = session.get(PurchaseRequest, purchase_request_id)
    if not purchase_request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    funding_allocations_data = update_data.funding_allocations or []
    budget_allocated = update_data.budget_allocated_for_the_order
    if funding_allocations_data:
        budget_allocated = sum(
            float(allocation.allocated_amount or 0)
            for allocation in funding_allocations_data
        )
    if budget_allocated <= 0:
        raise HTTPException(status_code=400, detail="Kwota wniosku musi byc wieksza od zera")
    if not update_data.used_cpv_id or update_data.used_cpv_id <= 0:
        raise HTTPException(status_code=400, detail="Kod CPV jest wymagany")

    if funding_allocations_data:
        for allocation in funding_allocations_data:
            if allocation.allocated_amount <= 0:
                raise HTTPException(status_code=400, detail="Kwota dofinansowania musi byc wieksza od zera")
            allocation_funding = session.get(Funding, allocation.funding_id)
            if not allocation_funding:
                raise HTTPException(status_code=404, detail="Dofinansowanie nie znalezione")

    plan = None
    plan_compliance_status = "compliant"
    justification = (update_data.plan_exception_justification or "").strip()
    if update_data.public_purchase_plan_id:
        plan = session.get(PublicPurchasePlan, update_data.public_purchase_plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Pozycja planu nie znaleziona")
        allocation_funding_ids = [allocation.funding_id for allocation in funding_allocations_data]
        if funding_allocations_data and plan.funding_id not in allocation_funding_ids:
            raise HTTPException(status_code=400, detail="Pozycja planu nie nalezy do wybranych dofinansowan")
        if not funding_allocations_data and plan.funding_id != purchase_request.funding_id:
            raise HTTPException(status_code=400, detail="Pozycja planu nie nalezy do dofinansowania")
        if plan.cpv_code != update_data.used_cpv_id:
            raise HTTPException(status_code=400, detail="Kod CPV nie zgadza sie z pozycja planu")
        used_from_plan = sum(
            request.budget_allocated_for_the_order
            for request in session.exec(
                select(PurchaseRequest).where(
                    PurchaseRequest.public_purchase_plan_id == plan.public_purchase_plan_id,
                    PurchaseRequest.purchase_request_id != purchase_request_id,
                )
            ).all()
        )
        if budget_allocated > plan.cost - used_from_plan:
            plan_compliance_status = "requires_approval"
    else:
        plan_compliance_status = "requires_approval"

    if plan_compliance_status == "requires_approval" and not justification:
        raise HTTPException(status_code=400, detail="Uzasadnienie odstepstwa jest wymagane")

    purchase_request.purchase_request_name = update_data.purchase_request_name
    purchase_request.budget_allocated_for_the_order = budget_allocated
    purchase_request.if_service = update_data.if_service
    purchase_request.used_cpv_id = update_data.used_cpv_id
    purchase_request.can_add = update_data.can_add
    purchase_request.public_purchase_plan_id = plan.public_purchase_plan_id if plan else None
    purchase_request.plan_exception_justification = justification or None
    purchase_request.plan_compliance_status = plan_compliance_status
    if funding_allocations_data:
        first_funding = session.get(Funding, funding_allocations_data[0].funding_id)
        if first_funding:
            purchase_request.funding_id = first_funding.funding_id
            purchase_request.project_budget_id = first_funding.project_budget_id
    if plan and not purchase_request.gslbccf_id:
        purchase_request.gslbccf_id = _ensure_group_for_plan(plan, session)

    if purchase_request.gslbccf_id:
        grouped_shops_list = session.get(
            GroupedShopsListByCpvCategoryAndFunding,
            purchase_request.gslbccf_id,
        )
        if grouped_shops_list:
            grouped_shops_list.allocated_money = budget_allocated
            session.add(grouped_shops_list)

    session.add(purchase_request)
    if funding_allocations_data:
        _replace_request_allocations(
            purchase_request.purchase_request_id,
            funding_allocations_data,
            session,
        )
    session.commit()
    session.refresh(purchase_request)
    return _purchase_request_out(purchase_request, session)


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
