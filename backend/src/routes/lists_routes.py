from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ListCreate(BaseModel):
    name: Optional[str] = None
    priority: int
    cost: float
    created_at: datetime
    funding_id: int
    funding_name: Optional[str] = None
    funding_total: float = 0.0
    funding_spent_money: float = 0.0
    funding_purchase_requests_total_allocated: float = 0.0
    funding_available_after_purchase_requests: float = 0.0
    shop_id: int
    student_id: int
    public_purchase_plan_id: Optional[int] = None
    purchase_request_id: Optional[int] = None
    gslbccf_id: Optional[int] = None

class ListItemCreate(BaseModel):
    item_id: int
    amount: int
    student_id: int

class ListClose(BaseModel):
    student_id: int

class ClosedPurchaseListForRequestOut(BaseModel):
    shop_purchase_list_id: int
    name: Optional[str] = None
    cost: float
    total_price: float
    item_count: int
    item_total: int
    created_at: datetime
    funding_id: int
    association_budget_id: Optional[int] = None
    association_budget_name: Optional[str] = None
    project_budget_id: Optional[int] = None
    project_budget_name: Optional[str] = None
    shop_id: int
    shop_name: Optional[str] = None
    settlement_id: int
    purchase_request_id: Optional[int] = None
    gslbccf_id: Optional[int] = None
    suggested_cpv_id: Optional[int] = None


def _cpv_to_int(cpv: Optional[str]) -> Optional[int]:
    if not cpv:
        return None
    try:
        return int(cpv.split("-")[0])
    except ValueError:
        return None


def _ensure_group_for_public_plan(public_plan: PublicPurchasePlan, session: Session) -> int:
    if public_plan.gslbccf_id:
        return public_plan.gslbccf_id

    grouped_shops_list = GroupedShopsListByCpvCategoryAndFunding(
        allocated_money=public_plan.cost
    )
    session.add(grouped_shops_list)
    session.commit()
    session.refresh(grouped_shops_list)

    public_plan.gslbccf_id = grouped_shops_list.gslbccf_id
    session.add(public_plan)
    session.commit()
    session.refresh(public_plan)
    return public_plan.gslbccf_id


def _public_plan_for_group(gslbccf_id: Optional[int], session: Session) -> Optional[PublicPurchasePlan]:
    if not gslbccf_id:
        return None
    return session.exec(
        select(PublicPurchasePlan).where(PublicPurchasePlan.gslbccf_id == gslbccf_id)
    ).first()


def _ensure_group_for_purchase_request(purchase_request: PurchaseRequest, session: Session) -> int:
    if purchase_request.gslbccf_id:
        return purchase_request.gslbccf_id

    grouped_shops_list = GroupedShopsListByCpvCategoryAndFunding(
        allocated_money=purchase_request.budget_allocated_for_the_order
    )
    session.add(grouped_shops_list)
    session.commit()
    session.refresh(grouped_shops_list)

    purchase_request.gslbccf_id = grouped_shops_list.gslbccf_id
    session.add(purchase_request)
    session.commit()
    session.refresh(purchase_request)
    return purchase_request.gslbccf_id


def _purchase_request_for_group(gslbccf_id: Optional[int], session: Session) -> Optional[PurchaseRequest]:
    if not gslbccf_id:
        return None
    return session.exec(
        select(PurchaseRequest).where(PurchaseRequest.gslbccf_id == gslbccf_id)
    ).first()


def _list_items_summary(shop_purchase_list_id: int, session: Session):
    line_items = session.exec(
        select(ShopPurchaseListItem).where(
            ShopPurchaseListItem.shop_purchase_list_id == shop_purchase_list_id
        )
    ).all()
    total_price = 0.0
    item_total = 0
    suggested_cpv_id = None
    contributed_students_id = set()
    last_contributor_id = None
    last_contribution_time = None
    
    for line in line_items:
        item = session.get(Item, line.item_id)
        if not item:
            continue

        total_price += (item.price or 0) * line.amount
        item_total += line.amount
        
        contributions = session.exec(
            select(ShopPurchaseListItemContribution).where(
                ShopPurchaseListItemContribution.shop_purchase_list_id == shop_purchase_list_id,
                ShopPurchaseListItemContribution.item_id == line.item_id
            )
        ).all()
        
        for c in contributions:
            contributed_students_id.add(c.student_id)
            if not last_contribution_time or c.created_at > last_contribution_time:
                last_contributor_id = c.student_id
                last_contribution_time = c.created_at

        if hasattr(line, 'last_edited_at') and line.last_edited_at:
            if not last_contribution_time or line.last_edited_at > last_contribution_time:
                last_contribution_time = line.last_edited_at
                last_contributor_id = getattr(line, 'last_edited_by_student_id', last_contributor_id)

        if suggested_cpv_id is None:
            subcategory = session.get(ProductSubcategory, item.product_subcategory_id)
            category = (
                session.get(ProductCategory, subcategory.product_category_id)
                if subcategory and subcategory.product_category_id
                else None
            )
            suggested_cpv_id = _cpv_to_int(category.cpv if category else None)

    return {
        "item_count": len(line_items),
        "item_total": item_total,
        "total_price": total_price,
        "suggested_cpv_id": suggested_cpv_id,
        "contributed_students_id": list(contributed_students_id),
        "last_contributor_id": last_contributor_id,
        "last_contribution_time": last_contribution_time,
    }


@app.get("/api/lists", response_model=List[dict])
def get_all_lists(
    student_id: Optional[int] = None,
    association_id: Optional[int] = None,
    shop_id: Optional[int] = None,
    public_purchase_plan_id: Optional[int] = None,
    purchase_request_id: Optional[int] = None,
    gslbccf_id: Optional[int] = None,
    open_only: bool = False,
    treasurer_view: bool = False,
    session: Session = Depends(get_session)
):
    statement = select(ShopPurchaseList)

    if treasurer_view:
        if not association_id:
            raise HTTPException(status_code=400, detail="Brak ID koła naukowego")
        statement = statement.join(Student).where(
            Student.association_id == association_id,
        )
    elif student_id:
        statement = statement.where(ShopPurchaseList.student_id == student_id)
    elif association_id:
        statement = statement.join(Student).where(
            Student.association_id == association_id,
        )

    if shop_id:
        statement = statement.where(ShopPurchaseList.shop_id == shop_id)

    if purchase_request_id:
        purchase_request = session.get(PurchaseRequest, purchase_request_id)
        if not purchase_request:
            raise HTTPException(status_code=404, detail="Zamowienie nie znalezione")
        if not purchase_request.gslbccf_id:
            return []
        statement = statement.where(ShopPurchaseList.gslbccf_id == purchase_request.gslbccf_id)
    elif public_purchase_plan_id:
        public_plan = session.get(PublicPurchasePlan, public_purchase_plan_id)
        if not public_plan:
            raise HTTPException(status_code=404, detail="Zamowienie publiczne nie znalezione")
        if not public_plan.gslbccf_id:
            return []
        statement = statement.where(ShopPurchaseList.gslbccf_id == public_plan.gslbccf_id)
    elif gslbccf_id:
        statement = statement.where(ShopPurchaseList.gslbccf_id == gslbccf_id)

    if open_only:
        statement = statement.where(ShopPurchaseList.settlement_id == None)

    statement = statement.order_by(ShopPurchaseList.shop_purchase_list_id.desc())
    lists = session.exec(statement).all()
    
    result = []
    for l in lists:
        summary = _list_items_summary(l.shop_purchase_list_id, session)
        public_plan = _public_plan_for_group(l.gslbccf_id, session)
        purchase_request = _purchase_request_for_group(l.gslbccf_id, session)
        list_dict = l.model_dump()
        list_dict.update({
            "last_contribution_time": summary["last_contribution_time"],
            "last_contributor": summary["last_contributor_id"],
            "contributed_students": summary["contributed_students_id"],
            "public_purchase_plan_id": public_plan.public_purchase_plan_id if public_plan else None,
            "public_purchase_plan_name": public_plan.public_purchase_plan_name if public_plan else None,
            "public_purchase_plan_cpv_code": public_plan.cpv_code if public_plan else None,
            "purchase_request_id": purchase_request.purchase_request_id if purchase_request else None,
            "purchase_request_name": purchase_request.purchase_request_name if purchase_request else None,
        })
        result.append(list_dict)
        
    return result


@app.post("/api/lists", response_model=ShopPurchaseList)
def create_purchase_list(new_list_data: ListCreate, session: Session = Depends(get_session)):
    creator = session.get(Student, new_list_data.student_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Student nie istnieje")
    funding = session.get(Funding, new_list_data.funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Dofinansowanie nie istnieje")
    project_budget = session.get(ProjectBudget, funding.project_budget_id)
    if not project_budget:
        raise HTTPException(status_code=400, detail="Dofinansowanie nie ma budżetu sekcji")
    project = session.get(Project, project_budget.project_id)
    if not project or project.association_id != creator.association_id:
        raise HTTPException(
            status_code=403,
            detail="Możesz wybrać tylko dofinansowanie sekcji swojego koła",
        )
    gslbccf_id = new_list_data.gslbccf_id
    if new_list_data.purchase_request_id:
        purchase_request = session.get(PurchaseRequest, new_list_data.purchase_request_id)
        if not purchase_request:
            raise HTTPException(status_code=404, detail="Zamowienie nie istnieje")
        if not purchase_request.can_add:
            raise HTTPException(status_code=400, detail="Zamowienie jest zamkniete dla nowych sklepow")
        if purchase_request.funding_id != funding.funding_id:
            raise HTTPException(
                status_code=400,
                detail="Zamowienie nie nalezy do wybranego dofinansowania",
            )
        request_project_budget = session.get(ProjectBudget, purchase_request.project_budget_id)
        request_project = (
            session.get(Project, request_project_budget.project_id)
            if request_project_budget
            else None
        )
        if not request_project or request_project.association_id != creator.association_id:
            raise HTTPException(
                status_code=403,
                detail="Zamowienie nie nalezy do kola uzytkownika",
            )
        gslbccf_id = _ensure_group_for_purchase_request(purchase_request, session)
    elif new_list_data.public_purchase_plan_id:
        public_plan = session.get(PublicPurchasePlan, new_list_data.public_purchase_plan_id)
        if not public_plan:
            raise HTTPException(status_code=404, detail="Zamowienie publiczne nie istnieje")
        if public_plan.funding_id != funding.funding_id:
            raise HTTPException(
                status_code=400,
                detail="Zamowienie publiczne nie nalezy do wybranego dofinansowania",
            )
        gslbccf_id = _ensure_group_for_public_plan(public_plan, session)
    elif not creator.project_finance_manager_id:
        raise HTTPException(
            status_code=403,
            detail="Zwykly uzytkownik musi wybrac zamowienie",
        )
    if funding.funding_price - funding.spent_money <= 0:
        raise HTTPException(status_code=400, detail="Wybrane dofinansowanie nie ma dostępnych środków")

    new_list = ShopPurchaseList(
        name=new_list_data.name,
        priority=new_list_data.priority,
        cost=new_list_data.cost,
        created_at=new_list_data.created_at,
        funding_id=new_list_data.funding_id,
        shop_id=new_list_data.shop_id,
        student_id=new_list_data.student_id,
        gslbccf_id=gslbccf_id
    )
    session.add(new_list)
    session.commit()
    session.refresh(new_list)
    return new_list


@app.patch("/api/lists/{list_id}/close", response_model=ShopPurchaseList)
def close_purchase_list(list_id: int, close_data: ListClose, session: Session = Depends(get_session)):
    list_to_close = session.get(ShopPurchaseList, list_id)
    if not list_to_close:
        raise HTTPException(status_code=404, detail="Lista nie znaleziona")

    if list_to_close.settlement_id is not None:
        raise HTTPException(status_code=400, detail="Lista jest już zamknięta")

    student = session.get(Student, close_data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student nie istnieje")
    if not student.project_finance_manager_id:
        raise HTTPException(status_code=403, detail="Tylko skarbnik może zamykać listy zamówień")
    if list_to_close.student_id != close_data.student_id:
        raise HTTPException(status_code=403, detail="Możesz zamknąć tylko listę utworzoną przez siebie")

    line_items = session.exec(
        select(ShopPurchaseListItem).where(ShopPurchaseListItem.shop_purchase_list_id == list_id)
    ).all()
    total_cost = 0.0
    for line in line_items:
        item = session.get(Item, line.item_id)
        if item:
            total_cost += (item.price or 0) * line.amount

    settlement = Settlement(
        created_at=datetime.now(),
        paid_by_project_finance_manager_id=student.project_finance_manager_id,
        purchase_request_id=None,
    )
    session.add(settlement)
    session.commit()
    session.refresh(settlement)

    list_to_close.settlement_id = settlement.settlement_id
    list_to_close.cost = total_cost
    session.add(list_to_close)
    session.commit()
    session.refresh(list_to_close)
    return list_to_close


@app.get("/api/lists/closed_for_purchase_requests", response_model=List[ClosedPurchaseListForRequestOut])
def get_closed_lists_for_purchase_requests(
    project_finance_manager_id: int,
    session: Session = Depends(get_session),
):
    statement = (
        select(ShopPurchaseList)
        .join(Student)
        .where(Student.project_finance_manager_id == project_finance_manager_id)
        .where(ShopPurchaseList.settlement_id != None)
        .order_by(ShopPurchaseList.shop_purchase_list_id.desc())
    )
    closed_lists = session.exec(statement).all()
    result = []

    for purchase_list in closed_lists:
        settlement = session.get(Settlement, purchase_list.settlement_id)
        if not settlement:
            continue

        funding = session.get(Funding, purchase_list.funding_id)
        association_budget = (
            session.get(AssociationBudget, funding.association_budget_id)
            if funding
            else None
        )
        shop = session.get(Shop, purchase_list.shop_id)
        project_budget = (
            session.get(ProjectBudget, funding.project_budget_id)
            if funding and funding.project_budget_id
            else None
        )
        items_summary = _list_items_summary(purchase_list.shop_purchase_list_id, session)
        total_price = items_summary["total_price"] or purchase_list.cost or 0.0
        funding_requests = (
            session.exec(
                select(PurchaseRequest).where(PurchaseRequest.funding_id == funding.funding_id)
            ).all()
            if funding
            else []
        )
        funding_allocated = sum(
            request.budget_allocated_for_the_order for request in funding_requests
        )

        result.append(
            ClosedPurchaseListForRequestOut(
                shop_purchase_list_id=purchase_list.shop_purchase_list_id,
                name=purchase_list.name,
                cost=purchase_list.cost,
                total_price=total_price,
                item_count=items_summary["item_count"],
                item_total=items_summary["item_total"],
                created_at=purchase_list.created_at,
                funding_id=purchase_list.funding_id,
                funding_name=funding.funding_name if funding else None,
                funding_total=funding.funding_price if funding else 0.0,
                funding_spent_money=funding.spent_money if funding else 0.0,
                funding_purchase_requests_total_allocated=funding_allocated,
                funding_available_after_purchase_requests=(
                    funding.funding_price - funding.spent_money - funding_allocated
                    if funding
                    else 0.0
                ),
                association_budget_id=association_budget.association_budget_id if association_budget else None,
                association_budget_name=association_budget.association_budget_name if association_budget else None,
                project_budget_id=project_budget.project_budget_id if project_budget else None,
                project_budget_name=project_budget.project_budget_name if project_budget else None,
                shop_id=purchase_list.shop_id,
                shop_name=shop.shop_name if shop else None,
                settlement_id=purchase_list.settlement_id,
                purchase_request_id=settlement.purchase_request_id,
                gslbccf_id=purchase_list.gslbccf_id,
                suggested_cpv_id=items_summary["suggested_cpv_id"],
            )
        )

    return result


@app.get("/api/lists/{list_id}", response_model=ShopPurchaseList)
def get_single_list(list_id: int, session: Session = Depends(get_session)):
    single_list = session.get(ShopPurchaseList, list_id)
    if not single_list:
        raise HTTPException(status_code=404, detail="Lista nie znaleziona")
    return single_list


@app.delete("/api/lists/{list_id}")
def delete_entire_list(list_id: int, session: Session = Depends(get_session)):
    list_to_delete = session.get(ShopPurchaseList, list_id)
    if not list_to_delete:
        raise HTTPException(status_code=404, detail="Lista nie znaleziona")

    items_on_list = session.exec(
        select(ShopPurchaseListItem).where(ShopPurchaseListItem.shop_purchase_list_id == list_id)
    ).all()

    for item in items_on_list:
        session.delete(item)

    session.delete(list_to_delete)
    session.commit()
    return {"status": "success"}


@app.get("/api/lists/{list_id}/items")
def get_items_for_list(
    list_id: int,
    student_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    statement = select(ShopPurchaseListItem).where(ShopPurchaseListItem.shop_purchase_list_id == list_id)
    line_items = session.exec(statement).all()
    results = []
    
    for line in line_items:
        item_details = session.get(Item, line.item_id)
        if item_details:
            current_student_amount = 0
            if student_id:
                contribution = session.get(
                    ShopPurchaseListItemContribution,
                    (list_id, line.item_id, student_id),
                )
                current_student_amount = contribution.amount if contribution else 0

            last_edited_by = getattr(line, 'last_edited_by_student_id', None)
            last_edited_time = getattr(line, 'last_edited_at', None)

            if not last_edited_by:
                latest_contribution = session.exec(
                    select(ShopPurchaseListItemContribution)
                    .where(
                        ShopPurchaseListItemContribution.shop_purchase_list_id == list_id,
                        ShopPurchaseListItemContribution.item_id == line.item_id
                    )
                    .order_by(ShopPurchaseListItemContribution.created_at.desc())
                ).first()
                if latest_contribution:
                    last_edited_by = latest_contribution.student_id
                    last_edited_time = latest_contribution.created_at

            results.append({
                "line_item_id": line.item_id,
                "item_id": item_details.item_id,
                "name": item_details.name,
                "price": item_details.price,
                "currency": item_details.currency,
                "amount": line.amount,
                "total_price": item_details.price * line.amount,
                "current_student_amount": current_student_amount,
                "can_remove_by_current_student": current_student_amount > 0,
                "student_id": last_edited_by if last_edited_by else item_details.student_id,
                "updated_at": last_edited_time.isoformat() if last_edited_time else item_details.created_at.isoformat() if item_details.created_at else None,
                "created_at": last_edited_time.isoformat() if last_edited_time else item_details.created_at.isoformat() if item_details.created_at else None
            })
            
    return results


@app.post("/api/lists/{list_id}/items")
def add_item_to_list(list_id: int, item_data: ListItemCreate, session: Session = Depends(get_session)):
    list_to_update = session.get(ShopPurchaseList, list_id)
    if not list_to_update:
        raise HTTPException(status_code=404, detail="Lista nie znaleziona")
    if list_to_update.settlement_id is not None:
        raise HTTPException(status_code=400, detail="Nie można dodawać pozycji do rozliczonej listy")
    if item_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Ilość musi być większa od zera")

    item = session.get(Item, item_data.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Przedmiot nie znaleziony")
    if item.status != "approved":
        raise HTTPException(status_code=400, detail="Można dodawać tylko zaakceptowane przedmioty")

    contributor = session.get(Student, item_data.student_id)
    if not contributor:
        raise HTTPException(status_code=404, detail="Student nie istnieje")

    try:
        now_time = datetime.now()
        existing_line_item = session.get(ShopPurchaseListItem, (list_id, item_data.item_id))
        if existing_line_item:
            existing_line_item.amount += item_data.amount
            if hasattr(existing_line_item, 'last_edited_by_student_id'):
                existing_line_item.last_edited_by_student_id = item_data.student_id
                existing_line_item.last_edited_at = now_time
            session.add(existing_line_item)
        else:
            existing_line_item = ShopPurchaseListItem(
                shop_purchase_list_id=list_id,
                item_id=item_data.item_id,
                amount=item_data.amount
            )
            if hasattr(existing_line_item, 'last_edited_by_student_id'):
                existing_line_item.last_edited_by_student_id = item_data.student_id
                existing_line_item.last_edited_at = now_time
            session.add(existing_line_item)

        contribution = session.get(
            ShopPurchaseListItemContribution,
            (list_id, item_data.item_id, item_data.student_id),
        )
        if contribution:
            contribution.amount += item_data.amount
            contribution.created_at = now_time
            session.add(contribution)
        else:
            contribution = ShopPurchaseListItemContribution(
                shop_purchase_list_id=list_id,
                item_id=item_data.item_id,
                student_id=item_data.student_id,
                amount=item_data.amount,
                created_at=now_time,
            )
            session.add(contribution)

        session.commit()
        return {"status": "success", "line_item_id": existing_line_item.item_id}
    except Exception as e:
        session.rollback()
        detailed_error = str(e)
        print(f"\n!!! BŁĄD BAZY DANYCH !!!\n{detailed_error}\n")
        raise HTTPException(status_code=400, detail=f"Baza odrzuciła wpis: {detailed_error}")


@app.delete("/api/lists/{list_id}/items/{item_id}")
def remove_item_from_list(
    list_id: int,
    item_id: int,
    student_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    list_to_update = session.get(ShopPurchaseList, list_id)
    if not list_to_update:
        raise HTTPException(status_code=404, detail="Lista nie znaleziona")
    if list_to_update.settlement_id is not None:
        raise HTTPException(status_code=400, detail="Nie można usuwać pozycji z zamkniętej listy")

    item_to_delete = session.get(ShopPurchaseListItem, (list_id, item_id))
    if not item_to_delete:
        raise HTTPException(status_code=404, detail="Pozycja nie znaleziona")

    if not student_id:
        raise HTTPException(status_code=400, detail="Brak ID studenta usuwającego pozycję")

    requester = session.get(Student, student_id)
    if not requester:
        raise HTTPException(status_code=404, detail="Student nie istnieje")

    can_manage_whole_item = (
        requester.project_finance_manager_id is not None
        and list_to_update.student_id == requester.student_id
    )

    if can_manage_whole_item:
        contributions = session.exec(
            select(ShopPurchaseListItemContribution).where(
                ShopPurchaseListItemContribution.shop_purchase_list_id == list_id,
                ShopPurchaseListItemContribution.item_id == item_id,
            )
        ).all()
        for contribution in contributions:
            session.delete(contribution)

        session.delete(item_to_delete)
        session.commit()
        return {"status": "success"}

    contribution = session.get(
        ShopPurchaseListItemContribution,
        (list_id, item_id, student_id),
    )
    if not contribution:
        raise HTTPException(status_code=403, detail="Możesz usunąć tylko pozycje dodane przez siebie")

    item_to_delete.amount -= contribution.amount
    if hasattr(item_to_delete, 'last_edited_by_student_id'):
        item_to_delete.last_edited_by_student_id = student_id
        item_to_delete.last_edited_at = datetime.now()

    session.delete(contribution)
    if item_to_delete.amount <= 0:
        session.delete(item_to_delete)
    else:
        session.add(item_to_delete)

    session.commit()
    return {"status": "success"}


@app.put("/api/lists/{list_id}/items/{item_id}")
def update_item_on_list(
    list_id: int,
    item_id: int,
    update_data: ListItemCreate,
    session: Session = Depends(get_session),
):
    list_to_update = session.get(ShopPurchaseList, list_id)
    if not list_to_update:
        raise HTTPException(status_code=404, detail="Lista nie znaleziona")
    if list_to_update.settlement_id is not None:
        raise HTTPException(status_code=400, detail="Nie można edytować pozycji na zamkniętej liście")

    line_item = session.get(ShopPurchaseListItem, (list_id, item_id))
    if not line_item:
        raise HTTPException(status_code=404, detail="Pozycja nie znaleziona")

    if update_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Ilość musi być większa od zera")

    student = session.get(Student, update_data.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student nie istnieje")

    contribution = session.get(
        ShopPurchaseListItemContribution,
        (list_id, item_id, update_data.student_id),
    )

    can_manage_whole_item = (
        student.project_finance_manager_id is not None
        and list_to_update.student_id == student.student_id
    )

    if not can_manage_whole_item and not contribution:
        raise HTTPException(status_code=403, detail="Brak uprawnień do edycji tej pozycji")

    now_time = datetime.now()
    if contribution:
        contribution.amount = update_data.amount
        contribution.created_at = now_time
        session.add(contribution)

    line_item.amount = update_data.amount
    if hasattr(line_item, 'last_edited_by_student_id'):
        line_item.last_edited_by_student_id = update_data.student_id
        line_item.last_edited_at = now_time
        
    session.add(line_item)
    session.commit()
    return {"status": "success"}
