from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field as PydanticField
from datetime import datetime, date



class PurchaseRequestFundingAllocationIn(BaseModel):
    funding_id: int
    allocated_amount: float


class PurchaseRequestPlanPositionIn(BaseModel):
    shop_purchase_list_id: Optional[int] = None
    public_purchase_plan_id: int
    allocated_amount: float


class PurchaseRequestCreate(BaseModel):
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[str]
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
    plan_positions: List[PurchaseRequestPlanPositionIn] = PydanticField(default_factory=list)


class PurchaseRequestUpdate(BaseModel):
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[str]
    can_add: bool = True
    public_purchase_plan_id: Optional[int] = None
    plan_exception_justification: Optional[str] = None
    funding_allocations: List[PurchaseRequestFundingAllocationIn] = PydanticField(default_factory=list)
    plan_positions: List[PurchaseRequestPlanPositionIn] = PydanticField(default_factory=list)


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
    cpv_code: str
    plan_position_number: Optional[str] = None
    description: Optional[str] = None
    planned_amount: float
    used_amount: float
    remaining_amount: float
    plan_year: int
    public_plan_list_name: Optional[str] = None
    plan_number: Optional[str] = None
    fund_responsible_person: Optional[str] = None
    shop_purchase_list_id: Optional[int] = None
    funding_id: Optional[int] = None
    funding_name: Optional[str] = None
    allocated_amount: Optional[float] = None
    product_category_id: Optional[int] = None
    product_category_name: Optional[str] = None


class PurchaseRequestOut(BaseModel):
    purchase_request_id: int
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[str] = None
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
    plan_positions: List[PurchasePlanPositionOut] = PydanticField(default_factory=list)
    plan_exception_justification: Optional[str] = None
    plan_compliance_status: str
    budget_info: Optional[PurchaseRequestBudgetOut] = None
    source_shop_purchase_list: Optional[SourceShopPurchaseListOut] = None
    funding_allocations: List[PurchaseRequestFundingAllocationOut] = PydanticField(default_factory=list)
    document_request_name: Optional[str] = None
    contract_value_date: Optional[date] = None
    euro_exchange_rate: Optional[float] = None
    main_cpv_code: Optional[str] = None
    final_net_total: Optional[float] = None
    final_gross_total: Optional[float] = None
    finalization_status: Optional[str] = None
    finalized_at: Optional[datetime] = None


class PurchaseRequestFinalizeIn(BaseModel):
    document_request_name: str
    euro_exchange_rate: float
    contract_value_date: date


class PurchaseRequestFinalizationDraftIn(BaseModel):
    document_request_name: Optional[str] = None
    euro_exchange_rate: Optional[float] = None
    contract_value_date: Optional[date] = None


class FinalizationCpvRowOut(BaseModel):
    cpv_code: str
    allocated_net_amount: float
    allocated_eur_amount: float = 0.0
    is_main_cpv: bool = False


class FinalizationPlanRowOut(BaseModel):
    public_purchase_plan_id: int
    plan_name: Optional[str] = None
    public_plan_list_name: Optional[str] = None
    plan_number: Optional[str] = None
    fund_responsible_person: Optional[str] = None
    funding_organizer: Optional[str] = None
    funding_signing_person: Optional[str] = None
    plan_position_number: Optional[str] = None
    cpv_code: Optional[str] = None
    funding_id: Optional[int] = None
    funding_name: Optional[str] = None
    planned_net_amount: float
    allocated_net_amount: float


class FinalizationFundingGrossRowOut(BaseModel):
    funding_id: Optional[int] = None
    funding_name: Optional[str] = None
    gross_amount: float


class FinalizationSnapshotRowOut(BaseModel):
    shop_purchase_list_id: Optional[int] = None
    shop_name: Optional[str] = None
    public_purchase_plan_id: Optional[int] = None
    cpv_code: Optional[str] = None
    plan_name: Optional[str] = None
    public_plan_list_name: Optional[str] = None
    plan_number: Optional[str] = None
    fund_responsible_person: Optional[str] = None
    funding_organizer: Optional[str] = None
    funding_signing_person: Optional[str] = None
    plan_position_number: Optional[str] = None
    funding_id: Optional[int] = None
    funding_name: Optional[str] = None
    planned_net_amount: float = 0.0
    allocated_net_amount: float = 0.0
    allocated_eur_amount: float = 0.0
    allocated_gross_amount: float = 0.0
    is_main_cpv: bool = False


class PurchaseRequestFinalizationOut(BaseModel):
    purchase_request_id: int
    document_request_name: Optional[str] = None
    contract_value_date: date
    euro_exchange_rate: Optional[float] = None
    main_cpv_code: Optional[str] = None
    net_total: float
    gross_total: float
    cpv_rows: List[FinalizationCpvRowOut] = PydanticField(default_factory=list)
    plan_rows: List[FinalizationPlanRowOut] = PydanticField(default_factory=list)
    funding_gross_rows: List[FinalizationFundingGrossRowOut] = PydanticField(default_factory=list)
    snapshot_rows: List[FinalizationSnapshotRowOut] = PydanticField(default_factory=list)


class PurchaseRequestSettlementLineOut(BaseModel):
    settlement_line_id: int
    purchase_request_id: int
    shop_purchase_list_id: Optional[int] = None
    invoice_id: Optional[int] = None
    invoice_number: Optional[str] = None
    shop_name: str
    purchase_description: Optional[str] = None
    planned_gross_amount: float = 0.0
    actual_gross_amount: Optional[float] = None
    difference_amount: float = 0.0
    is_extra: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None


class PurchaseRequestSettlementLineIn(BaseModel):
    settlement_line_id: Optional[int] = None
    shop_purchase_list_id: Optional[int] = None
    invoice_id: Optional[int] = None
    shop_name: str
    purchase_description: Optional[str] = None
    planned_gross_amount: float = 0.0
    actual_gross_amount: Optional[float] = None
    is_extra: bool = False


class PurchaseRequestSettlementLinesSaveIn(BaseModel):
    lines: List[PurchaseRequestSettlementLineIn] = PydanticField(default_factory=list)


class PurchaseRequestSettlementLinePatchIn(BaseModel):
    invoice_id: Optional[int] = None
    actual_gross_amount: Optional[float] = None
    shop_name: Optional[str] = None
    purchase_description: Optional[str] = None
    planned_gross_amount: Optional[float] = None


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


def _settlement_line_out(
    line: PurchaseRequestSettlementLine,
    session: Session,
) -> PurchaseRequestSettlementLineOut:
    invoice = session.get(Invoice, line.invoice_id) if line.invoice_id else None
    actual = line.actual_gross_amount
    planned = float(line.planned_gross_amount or 0)
    return PurchaseRequestSettlementLineOut(
        settlement_line_id=line.settlement_line_id,
        purchase_request_id=line.purchase_request_id,
        shop_purchase_list_id=line.shop_purchase_list_id,
        invoice_id=line.invoice_id,
        invoice_number=invoice.number if invoice else None,
        shop_name=line.shop_name,
        purchase_description=line.purchase_description,
        planned_gross_amount=planned,
        actual_gross_amount=actual,
        difference_amount=planned - float(actual or 0),
        is_extra=line.is_extra,
        created_at=line.created_at,
        updated_at=line.updated_at,
    )


def _line_description_for_purchase_list(
    purchase_list: ShopPurchaseList,
    session: Session,
) -> str:
    grouped: dict[str, float] = {}
    fallback_items: dict[str, float] = {}
    line_items = session.exec(
        select(ShopPurchaseListItem).where(
            ShopPurchaseListItem.shop_purchase_list_id
            == purchase_list.shop_purchase_list_id
        )
    ).all()
    for line_item in line_items:
        item = session.get(Item, line_item.item_id)
        if not item:
            continue
        gross = float(item.price or 0) * float(line_item.amount or 0)
        fallback_items[item.name] = fallback_items.get(item.name, 0.0) + gross
        subcategory = session.get(
            ProductSubcategory,
            item.product_subcategory_id,
        ) if item.product_subcategory_id else None
        category = session.get(
            ProductCategory,
            subcategory.product_category_id,
        ) if subcategory and subcategory.product_category_id else None
        label = (
            subcategory.product_subcategory_name
            if subcategory
            else (category.product_category_name if category else None)
        )
        if label:
            grouped[label] = grouped.get(label, 0.0) + gross

    source = grouped if grouped else fallback_items
    top_labels = [
        label for label, _ in sorted(
            source.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:3]
    ]
    return ", ".join(top_labels) if top_labels else (purchase_list.name or "Zakupy z koszyka")


def _ensure_settlement_lines_for_request(
    request: PurchaseRequest,
    session: Session,
) -> list[PurchaseRequestSettlementLine]:
    existing = session.exec(
        select(PurchaseRequestSettlementLine).where(
            PurchaseRequestSettlementLine.purchase_request_id
            == request.purchase_request_id
        )
    ).all()
    if existing:
        return existing

    for purchase_list in _request_purchase_lists(request, session):
        shop = session.get(Shop, purchase_list.shop_id)
        session.add(PurchaseRequestSettlementLine(
            purchase_request_id=request.purchase_request_id,
            shop_purchase_list_id=purchase_list.shop_purchase_list_id,
            shop_name=(
                shop.shop_name
                if shop
                else (purchase_list.name or f"Koszyk #{purchase_list.shop_purchase_list_id}")
            ),
            purchase_description=_line_description_for_purchase_list(
                purchase_list,
                session,
            ),
            planned_gross_amount=_shop_purchase_list_total(purchase_list, session),
            actual_gross_amount=None,
            is_extra=False,
            created_at=datetime.now(),
        ))
    session.commit()
    return session.exec(
        select(PurchaseRequestSettlementLine).where(
            PurchaseRequestSettlementLine.purchase_request_id
            == request.purchase_request_id
        )
    ).all()


def _settlement_lines_for_request(
    purchase_request_id: int,
    session: Session,
) -> list[PurchaseRequestSettlementLineOut]:
    lines = session.exec(
        select(PurchaseRequestSettlementLine).where(
            PurchaseRequestSettlementLine.purchase_request_id == purchase_request_id
        )
    ).all()
    return [_settlement_line_out(line, session) for line in lines]


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


def _used_amount_for_plan(
    public_purchase_plan_id: int,
    session: Session,
    excluded_purchase_request_id: Optional[int] = None,
) -> float:
    plan_rows_statement = select(PurchaseRequestPlanPosition).where(
        PurchaseRequestPlanPosition.public_purchase_plan_id == public_purchase_plan_id
    )
    if excluded_purchase_request_id:
        plan_rows_statement = plan_rows_statement.where(
            PurchaseRequestPlanPosition.purchase_request_id != excluded_purchase_request_id
        )
    plan_rows = session.exec(plan_rows_statement).all()
    linked_request_ids = {row.purchase_request_id for row in plan_rows}
    used_amount = sum(row.allocated_amount for row in plan_rows)

    legacy_statement = select(PurchaseRequest).where(
        PurchaseRequest.public_purchase_plan_id == public_purchase_plan_id
    )
    if excluded_purchase_request_id:
        legacy_statement = legacy_statement.where(
            PurchaseRequest.purchase_request_id != excluded_purchase_request_id
        )
    legacy_requests = session.exec(legacy_statement).all()
    used_amount += sum(
        request.budget_allocated_for_the_order
        for request in legacy_requests
        if request.purchase_request_id not in linked_request_ids
    )
    return used_amount


def _plan_position_out(
    plan: PublicPurchasePlan,
    session: Session,
    allocated_amount: Optional[float] = None,
    shop_purchase_list_id: Optional[int] = None,
    excluded_purchase_request_id: Optional[int] = None,
) -> PurchasePlanPositionOut:
    plan_list = session.get(
        PublicPurchasePlanList, plan.public_purchase_plan_list_id
    )
    funding = session.get(Funding, plan.funding_id) if plan.funding_id else None
    category = session.exec(
        select(ProductCategory).where(
            ProductCategory.public_purchase_plan_id == plan.public_purchase_plan_id
        )
    ).first()
    used_amount = _used_amount_for_plan(
        plan.public_purchase_plan_id,
        session,
        excluded_purchase_request_id,
    )
    return PurchasePlanPositionOut(
        public_purchase_plan_id=plan.public_purchase_plan_id,
        cpv_code=plan.cpv_code,
        plan_position_number=plan.plan_position_number,
        description=plan.public_purchase_plan_name,
        planned_amount=plan.cost,
        used_amount=used_amount,
        remaining_amount=plan.cost - used_amount,
        plan_year=plan_list.plan_year if plan_list else 0,
        public_plan_list_name=plan_list.public_plan_list_name if plan_list else None,
        plan_number=plan_list.plan_number if plan_list else None,
        fund_responsible_person=(
            plan_list.fund_responsible_person if plan_list else None
        ),
        shop_purchase_list_id=shop_purchase_list_id,
        funding_id=plan.funding_id,
        funding_name=funding.funding_name if funding else None,
        allocated_amount=allocated_amount,
        product_category_id=category.product_category_id if category else None,
        product_category_name=category.product_category_name if category else None,
    )


def _plan_positions_for_request(
    request: PurchaseRequest,
    session: Session,
) -> List[PurchasePlanPositionOut]:
    rows = session.exec(
        select(PurchaseRequestPlanPosition).where(
            PurchaseRequestPlanPosition.purchase_request_id
            == request.purchase_request_id
        )
    ).all()
    if rows:
        result = []
        for row in rows:
            plan = session.get(PublicPurchasePlan, row.public_purchase_plan_id)
            if plan:
                result.append(
                    _plan_position_out(
                        plan,
                        session,
                        row.allocated_amount,
                        row.shop_purchase_list_id,
                    )
                )
        return result

    if request.public_purchase_plan_id:
        plan = session.get(PublicPurchasePlan, request.public_purchase_plan_id)
        if plan:
            return [
                _plan_position_out(
                    plan,
                    session,
                    request.budget_allocated_for_the_order,
                    None,
                )
            ]
    return []


def _replace_request_plan_positions(
    purchase_request_id: int,
    positions_data: List[PurchaseRequestPlanPositionIn],
    session: Session,
):
    existing = session.exec(
        select(PurchaseRequestPlanPosition).where(
            PurchaseRequestPlanPosition.purchase_request_id == purchase_request_id
        )
    ).all()
    for position in existing:
        session.delete(position)

    merged: dict[tuple[int, int], float] = {}
    for position in positions_data:
        amount = float(position.allocated_amount or 0)
        if amount <= 0 or not position.shop_purchase_list_id:
            continue
        key = (position.shop_purchase_list_id, position.public_purchase_plan_id)
        merged[key] = (
            merged.get(key, 0.0) + amount
        )

    for (shop_purchase_list_id, public_purchase_plan_id), amount in merged.items():
        session.add(PurchaseRequestPlanPosition(
            purchase_request_id=purchase_request_id,
            shop_purchase_list_id=shop_purchase_list_id,
            public_purchase_plan_id=public_purchase_plan_id,
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
    plan_positions = _plan_positions_for_request(request, session)
    plan_position = plan_positions[0] if plan_positions else None

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
        plan_positions=plan_positions,
        plan_exception_justification=request.plan_exception_justification,
        plan_compliance_status=request.plan_compliance_status,
        budget_info=budget_info,
        source_shop_purchase_list=_source_list_for_request(request, session),
        funding_allocations=_allocations_for_request(request.purchase_request_id, session),
        document_request_name=request.document_request_name,
        contract_value_date=request.contract_value_date,
        euro_exchange_rate=request.euro_exchange_rate,
        main_cpv_code=request.main_cpv_code,
        final_net_total=request.final_net_total,
        final_gross_total=request.final_gross_total,
        finalization_status=request.finalization_status,
        finalized_at=request.finalized_at,
    )


def _request_purchase_lists(
    request: PurchaseRequest,
    session: Session,
) -> List[ShopPurchaseList]:
    if not request.gslbccf_id:
        return []
    return session.exec(
        select(ShopPurchaseList).where(
            ShopPurchaseList.gslbccf_id == request.gslbccf_id
        )
    ).all()


def _finalization_row_dicts(
    request: PurchaseRequest,
    session: Session,
    euro_rate: Optional[float] = None,
) -> list[dict]:
    rows = session.exec(
        select(PurchaseRequestPlanPosition).where(
            PurchaseRequestPlanPosition.purchase_request_id
            == request.purchase_request_id
        )
    ).all()
    result = []
    for row in rows:
        plan = session.get(PublicPurchasePlan, row.public_purchase_plan_id)
        if not plan:
            continue
        plan_list = session.get(
            PublicPurchasePlanList, plan.public_purchase_plan_list_id
        )
        funding = session.get(Funding, plan.funding_id) if plan.funding_id else None
        purchase_list = (
            session.get(ShopPurchaseList, row.shop_purchase_list_id)
            if row.shop_purchase_list_id
            else None
        )
        shop = session.get(Shop, purchase_list.shop_id) if purchase_list else None
        net_amount = float(row.allocated_amount or 0)
        gross_amount = net_amount * 1.23
        result.append({
            "shop_purchase_list_id": row.shop_purchase_list_id,
            "shop_name": shop.shop_name if shop else None,
            "public_purchase_plan_id": plan.public_purchase_plan_id,
            "cpv_code": plan.cpv_code,
            "plan_name": plan.public_purchase_plan_name,
            "public_plan_list_name": (
                plan_list.public_plan_list_name if plan_list else None
            ),
            "plan_number": plan_list.plan_number if plan_list else None,
            "fund_responsible_person": (
                (plan_list.fund_responsible_person if plan_list else None)
                or (funding.signing_person if funding else None)
            ),
            "funding_organizer": funding.organizer if funding else None,
            "funding_signing_person": funding.signing_person if funding else None,
            "plan_position_number": plan.plan_position_number,
            "funding_id": plan.funding_id,
            "funding_name": funding.funding_name if funding else None,
            "planned_net_amount": float(plan.cost or 0),
            "allocated_net_amount": net_amount,
            "allocated_eur_amount": (
                net_amount / euro_rate if euro_rate and euro_rate > 0 else 0.0
            ),
            "allocated_gross_amount": gross_amount,
            "is_main_cpv": False,
        })

    cpv_totals: dict[str, float] = {}
    for row in result:
        cpv_code = row["cpv_code"] or ""
        cpv_totals[cpv_code] = cpv_totals.get(cpv_code, 0.0) + row["allocated_net_amount"]
    main_cpv = (
        max(cpv_totals.items(), key=lambda item: item[1])[0]
        if cpv_totals
        else None
    )
    for row in result:
        row["is_main_cpv"] = bool(main_cpv and row["cpv_code"] == main_cpv)
    return result


def _default_euro_rate_for_request(
    request: PurchaseRequest,
    session: Session,
) -> Optional[float]:
    plan_rows = session.exec(
        select(PurchaseRequestPlanPosition).where(
            PurchaseRequestPlanPosition.purchase_request_id
            == request.purchase_request_id
        )
    ).all()
    for row in plan_rows:
        plan = session.get(PublicPurchasePlan, row.public_purchase_plan_id)
        if not plan:
            continue
        plan_list = session.get(
            PublicPurchasePlanList,
            plan.public_purchase_plan_list_id,
        )
        if plan_list and plan_list.euro_exchange_rate:
            return plan_list.euro_exchange_rate
    return request.euro_exchange_rate


def _finalization_summary(
    request: PurchaseRequest,
    session: Session,
    euro_rate: Optional[float] = None,
    value_date: Optional[date] = None,
) -> PurchaseRequestFinalizationOut:
    euro_rate = euro_rate or _default_euro_rate_for_request(request, session)
    rows = _finalization_row_dicts(request, session, euro_rate)
    cpv_totals: dict[str, float] = {}
    for row in rows:
        cpv_code = row["cpv_code"] or ""
        cpv_totals[cpv_code] = cpv_totals.get(cpv_code, 0.0) + row["allocated_net_amount"]
    main_cpv = (
        max(cpv_totals.items(), key=lambda item: item[1])[0]
        if cpv_totals
        else None
    )
    cpv_rows = [
        FinalizationCpvRowOut(
            cpv_code=cpv_code,
            allocated_net_amount=net_amount,
            allocated_eur_amount=(
                net_amount / euro_rate if euro_rate and euro_rate > 0 else 0.0
            ),
            is_main_cpv=cpv_code == main_cpv,
        )
        for cpv_code, net_amount in sorted(cpv_totals.items())
    ]

    plan_totals: dict[int, dict] = {}
    funding_gross_totals: dict[Optional[int], dict] = {}
    for row in rows:
        plan_id = row["public_purchase_plan_id"]
        if plan_id not in plan_totals:
            plan_totals[plan_id] = {**row, "allocated_net_amount": 0.0}
        plan_totals[plan_id]["allocated_net_amount"] += row["allocated_net_amount"]

        funding_id = row["funding_id"]
        if funding_id not in funding_gross_totals:
            funding_gross_totals[funding_id] = {
                "funding_id": funding_id,
                "funding_name": row["funding_name"],
                "gross_amount": 0.0,
            }
        funding_gross_totals[funding_id]["gross_amount"] += row["allocated_gross_amount"]

    return PurchaseRequestFinalizationOut(
        purchase_request_id=request.purchase_request_id,
        document_request_name=request.document_request_name or request.purchase_request_name,
        contract_value_date=value_date or request.contract_value_date or date.today(),
        euro_exchange_rate=euro_rate or request.euro_exchange_rate,
        main_cpv_code=main_cpv,
        net_total=sum(row["allocated_net_amount"] for row in rows),
        gross_total=sum(row["allocated_gross_amount"] for row in rows),
        cpv_rows=cpv_rows,
        plan_rows=[
            FinalizationPlanRowOut(
                public_purchase_plan_id=row["public_purchase_plan_id"],
                plan_name=row["plan_name"],
                public_plan_list_name=row["public_plan_list_name"],
                plan_number=row["plan_number"],
                fund_responsible_person=row["fund_responsible_person"],
                funding_organizer=row["funding_organizer"],
                funding_signing_person=row["funding_signing_person"],
                plan_position_number=row["plan_position_number"],
                cpv_code=row["cpv_code"],
                funding_id=row["funding_id"],
                funding_name=row["funding_name"],
                planned_net_amount=row["planned_net_amount"],
                allocated_net_amount=row["allocated_net_amount"],
            )
            for row in plan_totals.values()
        ],
        funding_gross_rows=[
            FinalizationFundingGrossRowOut(**row)
            for row in funding_gross_totals.values()
        ],
        snapshot_rows=[FinalizationSnapshotRowOut(**row) for row in rows],
    )


def _ensure_request_can_be_finalized(
    request: PurchaseRequest,
    session: Session,
) -> list[ShopPurchaseList]:
    purchase_lists = _request_purchase_lists(request, session)
    if not purchase_lists:
        raise HTTPException(status_code=400, detail="Wniosek nie ma koszykow do zamkniecia")
    plan_rows = session.exec(
        select(PurchaseRequestPlanPosition).where(
            PurchaseRequestPlanPosition.purchase_request_id
            == request.purchase_request_id
        )
    ).all()
    if not plan_rows:
        raise HTTPException(status_code=400, detail="Wniosek nie ma przypisanych pozycji CPV")
    return purchase_lists


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


@app.post(
    "/api/purchase_requests/{purchase_request_id}/prepare_finalization",
    response_model=PurchaseRequestFinalizationOut,
)
def prepare_purchase_request_finalization(
    purchase_request_id: int,
    session: Session = Depends(get_session),
):
    request = session.get(PurchaseRequest, purchase_request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    if request.finalization_status in ("finalized", "accounting_pending", "settlement"):
        _ensure_settlement_lines_for_request(request, session)
        return _finalization_summary(
            request,
            session,
            request.euro_exchange_rate,
            request.contract_value_date,
        )

    purchase_lists = _ensure_request_can_be_finalized(request, session)
    for purchase_list in purchase_lists:
        total_cost = _shop_purchase_list_total(purchase_list, session)
        if purchase_list.settlement_id:
            settlement = session.get(Settlement, purchase_list.settlement_id)
            if settlement:
                settlement.purchase_request_id = request.purchase_request_id
                session.add(settlement)
        else:
            settlement = Settlement(
                created_at=datetime.now(),
                paid_by_project_finance_manager_id=request.project_finance_manager_id,
                purchase_request_id=request.purchase_request_id,
            )
            session.add(settlement)
            session.flush()
            purchase_list.settlement_id = settlement.settlement_id
        purchase_list.cost = total_cost
        session.add(purchase_list)

    request.can_add = False
    request.finalization_status = "prepared"
    session.add(request)
    session.commit()
    session.refresh(request)
    return _finalization_summary(request, session)


@app.patch(
    "/api/purchase_requests/{purchase_request_id}/finalization_draft",
    response_model=PurchaseRequestFinalizationOut,
)
def save_purchase_request_finalization_draft(
    purchase_request_id: int,
    draft_data: PurchaseRequestFinalizationDraftIn,
    session: Session = Depends(get_session),
):
    request = session.get(PurchaseRequest, purchase_request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    if request.finalization_status not in ("prepared", "draft"):
        raise HTTPException(status_code=400, detail="Szkic mozna zapisac tylko przed finalnym zatwierdzeniem")

    if draft_data.document_request_name is not None:
        request.document_request_name = (draft_data.document_request_name or "").strip() or None
    if draft_data.euro_exchange_rate is not None:
        if draft_data.euro_exchange_rate <= 0:
            raise HTTPException(status_code=400, detail="Kurs euro musi byc wiekszy od zera")
        request.euro_exchange_rate = draft_data.euro_exchange_rate
    if draft_data.contract_value_date is not None:
        request.contract_value_date = draft_data.contract_value_date
    if request.finalization_status == "draft":
        request.finalization_status = "prepared"
    request.can_add = False
    session.add(request)
    session.commit()
    session.refresh(request)
    return _finalization_summary(
        request,
        session,
        request.euro_exchange_rate,
        request.contract_value_date,
    )


@app.post(
    "/api/purchase_requests/{purchase_request_id}/finalize",
    response_model=PurchaseRequestFinalizationOut,
)
def finalize_purchase_request(
    purchase_request_id: int,
    finalization_data: PurchaseRequestFinalizeIn,
    session: Session = Depends(get_session),
):
    request = session.get(PurchaseRequest, purchase_request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    if finalization_data.euro_exchange_rate <= 0:
        raise HTTPException(status_code=400, detail="Kurs euro musi byc wiekszy od zera")
    document_name = (finalization_data.document_request_name or "").strip()
    if not document_name:
        raise HTTPException(status_code=400, detail="Nazwa wniosku na dokumencie jest wymagana")

    purchase_lists = _ensure_request_can_be_finalized(request, session)
    for purchase_list in purchase_lists:
        if not purchase_list.settlement_id:
            settlement = Settlement(
                created_at=datetime.now(),
                paid_by_project_finance_manager_id=request.project_finance_manager_id,
                purchase_request_id=request.purchase_request_id,
            )
            session.add(settlement)
            session.flush()
            purchase_list.settlement_id = settlement.settlement_id
        else:
            settlement = session.get(Settlement, purchase_list.settlement_id)
            if settlement:
                settlement.purchase_request_id = request.purchase_request_id
                session.add(settlement)
        purchase_list.cost = _shop_purchase_list_total(purchase_list, session)
        session.add(purchase_list)

    summary = _finalization_summary(
        request,
        session,
        finalization_data.euro_exchange_rate,
        finalization_data.contract_value_date,
    )
    if not summary.snapshot_rows:
        raise HTTPException(status_code=400, detail="Brak pozycji CPV do zapisania")

    existing_snapshots = session.exec(
        select(PurchaseRequestFinalizationSnapshot).where(
            PurchaseRequestFinalizationSnapshot.purchase_request_id
            == request.purchase_request_id
        )
    ).all()
    for snapshot in existing_snapshots:
        session.delete(snapshot)

    for row in summary.snapshot_rows:
        session.add(PurchaseRequestFinalizationSnapshot(
            purchase_request_id=request.purchase_request_id,
            shop_purchase_list_id=row.shop_purchase_list_id,
            public_purchase_plan_id=row.public_purchase_plan_id,
            funding_id=row.funding_id,
            shop_name=row.shop_name,
            funding_name=row.funding_name,
            plan_name=row.plan_name,
            plan_number=row.plan_number,
            fund_responsible_person=row.fund_responsible_person,
            plan_position_number=row.plan_position_number,
            cpv_code=row.cpv_code,
            planned_net_amount=row.planned_net_amount,
            allocated_net_amount=row.allocated_net_amount,
            allocated_eur_amount=row.allocated_eur_amount,
            allocated_gross_amount=row.allocated_gross_amount,
            is_main_cpv=row.is_main_cpv,
            created_at=datetime.now(),
        ))

    request.document_request_name = document_name
    request.contract_value_date = finalization_data.contract_value_date
    request.euro_exchange_rate = finalization_data.euro_exchange_rate
    request.main_cpv_code = summary.main_cpv_code
    request.used_cpv_id = summary.main_cpv_code
    request.final_net_total = summary.net_total
    request.final_gross_total = summary.gross_total
    request.budget_allocated_for_the_order = summary.gross_total
    request.can_add = False
    request.finalization_status = "accounting_pending"
    request.finalized_at = datetime.now()
    session.add(request)

    _replace_request_allocations(
        request.purchase_request_id,
        [
            PurchaseRequestFundingAllocationIn(
                funding_id=row.funding_id,
                allocated_amount=row.gross_amount,
            )
            for row in summary.funding_gross_rows
            if row.funding_id
        ],
        session,
    )

    session.commit()
    session.refresh(request)
    _ensure_settlement_lines_for_request(request, session)
    return _finalization_summary(
        request,
        session,
        finalization_data.euro_exchange_rate,
        finalization_data.contract_value_date,
    )


@app.get(
    "/api/purchase_requests/{purchase_request_id}/settlement_lines",
    response_model=List[PurchaseRequestSettlementLineOut],
)
def get_purchase_request_settlement_lines(
    purchase_request_id: int,
    session: Session = Depends(get_session),
):
    request = session.get(PurchaseRequest, purchase_request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    _ensure_settlement_lines_for_request(request, session)
    return _settlement_lines_for_request(purchase_request_id, session)


@app.put(
    "/api/purchase_requests/{purchase_request_id}/settlement_lines",
    response_model=List[PurchaseRequestSettlementLineOut],
)
def save_purchase_request_settlement_lines(
    purchase_request_id: int,
    payload: PurchaseRequestSettlementLinesSaveIn,
    session: Session = Depends(get_session),
):
    request = session.get(PurchaseRequest, purchase_request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    if request.finalization_status == "settlement":
        raise HTTPException(
            status_code=400,
            detail="Planowane pozycje mozna zmieniac przed przekazaniem do rozliczen",
        )

    existing = {
        line.settlement_line_id: line
        for line in session.exec(
            select(PurchaseRequestSettlementLine).where(
                PurchaseRequestSettlementLine.purchase_request_id
                == purchase_request_id
            )
        ).all()
    }
    seen_ids = set()
    for line_data in payload.lines:
        shop_name = (line_data.shop_name or "").strip()
        if not shop_name:
            raise HTTPException(status_code=400, detail="Nazwa sklepu jest wymagana")
        planned_amount = float(line_data.planned_gross_amount or 0)
        if planned_amount < 0:
            raise HTTPException(status_code=400, detail="Kwota planowana nie moze byc ujemna")
        line = existing.get(line_data.settlement_line_id)
        if not line:
            line = PurchaseRequestSettlementLine(
                purchase_request_id=purchase_request_id,
                shop_name=shop_name,
                created_at=datetime.now(),
            )
        line.shop_purchase_list_id = line_data.shop_purchase_list_id
        line.invoice_id = line_data.invoice_id
        line.shop_name = shop_name
        line.purchase_description = (line_data.purchase_description or "").strip() or None
        line.planned_gross_amount = planned_amount
        line.actual_gross_amount = line_data.actual_gross_amount
        line.is_extra = line_data.is_extra
        line.updated_at = datetime.now()
        session.add(line)
        session.flush()
        seen_ids.add(line.settlement_line_id)

    for line_id, line in existing.items():
        if line_id not in seen_ids:
            session.delete(line)

    session.commit()
    return _settlement_lines_for_request(purchase_request_id, session)


@app.post(
    "/api/purchase_requests/{purchase_request_id}/send_to_settlement",
    response_model=PurchaseRequestOut,
)
def send_purchase_request_to_settlement(
    purchase_request_id: int,
    session: Session = Depends(get_session),
):
    request = session.get(PurchaseRequest, purchase_request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    if request.finalization_status not in ("accounting_pending", "settlement"):
        raise HTTPException(
            status_code=400,
            detail="Do rozliczen mozna przekazac tylko zatwierdzony wniosek",
        )
    lines = _ensure_settlement_lines_for_request(request, session)
    if not lines:
        raise HTTPException(status_code=400, detail="Brak pozycji do rozliczenia")
    settlements = session.exec(
        select(Settlement).where(
            Settlement.purchase_request_id == purchase_request_id
        )
    ).all()
    if not settlements:
        settlement = Settlement(
            created_at=datetime.now(),
            paid_by_project_finance_manager_id=request.project_finance_manager_id,
            purchase_request_id=purchase_request_id,
        )
        session.add(settlement)
    request.can_add = False
    request.finalization_status = "settlement"
    session.add(request)
    session.commit()
    session.refresh(request)
    return _purchase_request_out(request, session)


@app.patch(
    "/api/purchase_request_settlement_lines/{settlement_line_id}",
    response_model=PurchaseRequestSettlementLineOut,
)
def update_purchase_request_settlement_line(
    settlement_line_id: int,
    payload: PurchaseRequestSettlementLinePatchIn,
    session: Session = Depends(get_session),
):
    line = session.get(PurchaseRequestSettlementLine, settlement_line_id)
    if not line:
        raise HTTPException(status_code=404, detail="Pozycja rozliczenia nie znaleziona")
    if "invoice_id" in payload.model_fields_set:
        if payload.invoice_id is not None:
            invoice = session.get(Invoice, payload.invoice_id)
            if not invoice:
                raise HTTPException(status_code=404, detail="Faktura nie znaleziona")
        line.invoice_id = payload.invoice_id
    if payload.actual_gross_amount is not None:
        if payload.actual_gross_amount < 0:
            raise HTTPException(status_code=400, detail="Kwota faktyczna nie moze byc ujemna")
        line.actual_gross_amount = payload.actual_gross_amount
    if payload.shop_name is not None:
        shop_name = payload.shop_name.strip()
        if not shop_name:
            raise HTTPException(status_code=400, detail="Nazwa sklepu jest wymagana")
        line.shop_name = shop_name
    if payload.purchase_description is not None:
        line.purchase_description = payload.purchase_description.strip() or None
    if payload.planned_gross_amount is not None:
        if payload.planned_gross_amount < 0:
            raise HTTPException(status_code=400, detail="Kwota planowana nie moze byc ujemna")
        line.planned_gross_amount = payload.planned_gross_amount
    line.updated_at = datetime.now()
    session.add(line)
    session.commit()
    session.refresh(line)
    return _settlement_line_out(line, session)


@app.post(
    "/api/purchase_requests/{purchase_request_id}/settlement_lines/extra",
    response_model=PurchaseRequestSettlementLineOut,
)
def add_extra_purchase_request_settlement_line(
    purchase_request_id: int,
    payload: PurchaseRequestSettlementLineIn,
    session: Session = Depends(get_session),
):
    request = session.get(PurchaseRequest, purchase_request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    if request.finalization_status != "settlement":
        raise HTTPException(
            status_code=400,
            detail="Dodatkowe pozycje mozna dodawac po przekazaniu wniosku do rozliczen",
        )
    shop_name = (payload.shop_name or "").strip()
    if not shop_name:
        raise HTTPException(status_code=400, detail="Nazwa sklepu jest wymagana")
    actual_amount = payload.actual_gross_amount
    if actual_amount is None:
        actual_amount = payload.planned_gross_amount
    if actual_amount is None or actual_amount < 0:
        raise HTTPException(status_code=400, detail="Kwota faktyczna jest wymagana")
    line = PurchaseRequestSettlementLine(
        purchase_request_id=purchase_request_id,
        shop_name=shop_name,
        purchase_description=(payload.purchase_description or "").strip() or None,
        planned_gross_amount=float(payload.planned_gross_amount or 0),
        actual_gross_amount=float(actual_amount),
        invoice_id=payload.invoice_id,
        is_extra=True,
        created_at=datetime.now(),
    )
    session.add(line)
    session.commit()
    session.refresh(line)
    return _settlement_line_out(line, session)


@app.post(
    "/api/purchase_requests/{purchase_request_id}/return_to_open",
    response_model=PurchaseRequestOut,
)
def return_purchase_request_to_open(
    purchase_request_id: int,
    session: Session = Depends(get_session),
):
    request = session.get(PurchaseRequest, purchase_request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")
    if request.finalization_status != "prepared":
        raise HTTPException(
            status_code=400,
            detail="Do otwartych mozna cofnac tylko wniosek do dokonczenia",
        )

    settlement_ids = []
    for purchase_list in _request_purchase_lists(request, session):
        if purchase_list.settlement_id:
            settlement_ids.append(purchase_list.settlement_id)
            purchase_list.settlement_id = None
            session.add(purchase_list)

    session.flush()
    for settlement_id in set(settlement_ids):
        settlement = session.get(Settlement, settlement_id)
        if not settlement:
            continue
        invoices = session.exec(
            select(Invoice).where(Invoice.settlement_id == settlement_id)
        ).all()
        linked_lists = session.exec(
            select(ShopPurchaseList).where(
                ShopPurchaseList.settlement_id == settlement_id
            )
        ).all()
        if invoices or linked_lists:
            settlement.purchase_request_id = None
            session.add(settlement)
        elif settlement.purchase_request_id == request.purchase_request_id:
            session.delete(settlement)

    request.can_add = True
    request.finalization_status = "draft"
    request.finalized_at = None
    session.add(request)
    session.commit()
    session.refresh(request)
    return _purchase_request_out(request, session)


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
        if budget_allocated <= 0:
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
    plan = None
    selected_plans: list[tuple[PurchaseRequestPlanPositionIn, PublicPurchasePlan, float]] = []
    plan_positions_data = new_purchase_request_data.plan_positions or []
    if not plan_positions_data and new_purchase_request_data.public_purchase_plan_id:
        plan_positions_data = [
            PurchaseRequestPlanPositionIn(
                public_purchase_plan_id=new_purchase_request_data.public_purchase_plan_id,
                allocated_amount=budget_allocated,
            )
        ]
    plan_compliance_status = "draft" if is_draft else "compliant"
    justification = (
        new_purchase_request_data.plan_exception_justification or ""
    ).strip()
    allocation_funding_ids = {
        allocation.funding_id for allocation in funding_allocations_data
    } or {funding.funding_id}
    selected_amounts_by_plan: dict[int, float] = {}
    for plan_position_data in plan_positions_data:
        amount = float(plan_position_data.allocated_amount or 0)
        if amount <= 0:
            continue
        selected_plan = session.get(
            PublicPurchasePlan,
            plan_position_data.public_purchase_plan_id,
        )
        if not selected_plan:
            raise HTTPException(
                status_code=404, detail="Pozycja planu zamówień nie znaleziona"
            )
        if selected_plan.funding_id not in allocation_funding_ids:
            raise HTTPException(
                status_code=400,
                detail="Pozycja planu nie należy do dofinansowania zamówienia",
            )
        if not selected_plan.cpv_code:
            raise HTTPException(
                status_code=400,
                detail="Kod CPV wniosku nie zgadza się z pozycją planu",
            )
        selected_total_for_plan = (
            selected_amounts_by_plan.get(selected_plan.public_purchase_plan_id, 0.0)
            + amount
        )
        used_from_plan = _used_amount_for_plan(
            selected_plan.public_purchase_plan_id,
            session,
        )
        if selected_total_for_plan > selected_plan.cost - used_from_plan:
            plan_compliance_status = "requires_approval"
        selected_amounts_by_plan[selected_plan.public_purchase_plan_id] = selected_total_for_plan
        selected_plans.append((plan_position_data, selected_plan, amount))

    if selected_plans:
        plan = selected_plans[0][1]
    if not selected_plans:
        plan_compliance_status = "draft"

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
        used_cpv_id = plan.cpv_code if plan else (new_purchase_request_data.used_cpv_id or None),
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
        _replace_request_plan_positions(
            new_purchase_request.purchase_request_id,
            [
                PurchaseRequestPlanPositionIn(
                    shop_purchase_list_id=plan_position_data.shop_purchase_list_id,
                    public_purchase_plan_id=selected_plan.public_purchase_plan_id,
                    allocated_amount=amount,
                )
                for plan_position_data, selected_plan, amount in selected_plans
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
        if budget_allocated <= 0:
            budget_allocated = sum(
                float(allocation.allocated_amount or 0)
                for allocation in funding_allocations_data
            )
    is_draft = budget_allocated <= 0

    if funding_allocations_data:
        for allocation in funding_allocations_data:
            if allocation.allocated_amount <= 0:
                raise HTTPException(status_code=400, detail="Kwota dofinansowania musi byc wieksza od zera")
            allocation_funding = session.get(Funding, allocation.funding_id)
            if not allocation_funding:
                raise HTTPException(status_code=404, detail="Dofinansowanie nie znalezione")

    plan = None
    selected_plans: list[tuple[PurchaseRequestPlanPositionIn, PublicPurchasePlan, float]] = []
    plan_positions_data = update_data.plan_positions or []
    if not plan_positions_data and update_data.public_purchase_plan_id:
        plan_positions_data = [
            PurchaseRequestPlanPositionIn(
                public_purchase_plan_id=update_data.public_purchase_plan_id,
                allocated_amount=budget_allocated,
            )
        ]
    plan_compliance_status = "draft" if is_draft or not plan_positions_data else "compliant"
    justification = (update_data.plan_exception_justification or "").strip()

    allocation_funding_ids = {
        allocation.funding_id for allocation in funding_allocations_data
    } or {purchase_request.funding_id}
    selected_amounts_by_plan: dict[int, float] = {}
    for plan_position_data in plan_positions_data:
        amount = float(plan_position_data.allocated_amount or 0)
        if amount <= 0:
            continue
        selected_plan = session.get(
            PublicPurchasePlan,
            plan_position_data.public_purchase_plan_id,
        )
        if not selected_plan:
            raise HTTPException(status_code=404, detail="Pozycja planu nie znaleziona")
        if selected_plan.funding_id not in allocation_funding_ids:
            raise HTTPException(status_code=400, detail="Pozycja planu nie nalezy do wybranych dofinansowan")
        selected_total_for_plan = (
            selected_amounts_by_plan.get(selected_plan.public_purchase_plan_id, 0.0)
            + amount
        )
        used_from_plan = _used_amount_for_plan(
            selected_plan.public_purchase_plan_id,
            session,
            purchase_request_id,
        )
        if selected_total_for_plan > selected_plan.cost - used_from_plan:
            plan_compliance_status = "requires_approval"
        selected_amounts_by_plan[selected_plan.public_purchase_plan_id] = selected_total_for_plan
        selected_plans.append((plan_position_data, selected_plan, amount))

    if selected_plans:
        plan = selected_plans[0][1]

    if plan_compliance_status == "requires_approval" and not justification:
        raise HTTPException(status_code=400, detail="Uzasadnienie odstepstwa jest wymagane")

    purchase_request.purchase_request_name = update_data.purchase_request_name
    purchase_request.budget_allocated_for_the_order = budget_allocated
    purchase_request.if_service = update_data.if_service
    purchase_request.used_cpv_id = plan.cpv_code if plan else (update_data.used_cpv_id or None)
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
    _replace_request_plan_positions(
        purchase_request.purchase_request_id,
        [
            PurchaseRequestPlanPositionIn(
                shop_purchase_list_id=plan_position_data.shop_purchase_list_id,
                public_purchase_plan_id=selected_plan.public_purchase_plan_id,
                allocated_amount=amount,
            )
            for plan_position_data, selected_plan, amount in selected_plans
        ],
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
