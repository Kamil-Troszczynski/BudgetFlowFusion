from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date


class InvoiceOut(BaseModel):
    invoice_id: int
    number: Optional[str] = None
    invoice_name: Optional[str] = None
    issue_date: Optional[date] = None
    seller_name: Optional[str] = None
    seller_nip: Optional[str] = None
    net_total: Optional[float] = None
    vat_total: Optional[float] = None
    status: Optional[str] = None
    amount: Optional[float] = None
    created_at: Optional[datetime] = None
    project_finance_manager_id: Optional[int] = None
    project_finance_manager_name: Optional[str] = None
    settlement_id: Optional[int] = None
    purchase_request_id: Optional[int] = None
    purchase_request_name: Optional[str] = None


class PurchaseRequestOut(BaseModel):
    purchase_request_id: int
    purchase_request_name: Optional[str] = None
    budget_allocated_for_the_order: Optional[float] = None
    if_service: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class ShopPurchaseListOut(BaseModel):
    shop_purchase_list_id: int
    model_config = ConfigDict(from_attributes=True)


class SettlementLineOut(BaseModel):
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


class SettlementOut(BaseModel):
    settlement_id: int
    created_at: datetime
    paid_by_project_finance_manager_id: Optional[int] = None
    purchase_request_id: Optional[int] = None
    purchase_request: Optional[PurchaseRequestOut] = None
    invoices: List[InvoiceOut] = []
    shop_purchase_lists: List[ShopPurchaseListOut] = []
    settlement_lines: List[SettlementLineOut] = []
    total_spent: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class SettlementCreate(BaseModel):
    created_at: datetime
    paid_by_project_finance_manager_id: Optional[int] = None
    purchase_request_id: Optional[int] = None


class InvoiceCreate(BaseModel):
    number: str
    issue_date: date
    seller_name: str
    seller_nip: str
    net_total: float
    vat_total: float
    status: InvoiceStatus = InvoiceStatus.pending
    project_finance_manager_id: Optional[int] = None


class InvoiceUpdate(BaseModel):
    number: Optional[str] = None
    issue_date: Optional[date] = None
    seller_name: Optional[str] = None
    seller_nip: Optional[str] = None
    net_total: Optional[float] = None
    vat_total: Optional[float] = None
    status: Optional[InvoiceStatus] = None
    project_finance_manager_id: Optional[int] = None


class SettlementStatusUpdate(BaseModel):
    status: str


def _manager_name(project_finance_manager_id: Optional[int], session: Session) -> Optional[str]:
    if not project_finance_manager_id:
        return None
    student = session.exec(
        select(Student).where(
            Student.project_finance_manager_id == project_finance_manager_id
        )
    ).first()
    if student:
        return f"{student.name} {student.surname}".strip()
    manager = session.get(ProjectFinanceManager, project_finance_manager_id)
    return manager.login if manager else None


def _invoice_out(
    invoice: Invoice,
    session: Session,
    settlement: Optional[Settlement] = None,
    purchase_request: Optional[PurchaseRequest] = None,
) -> InvoiceOut:
    if settlement is None and invoice.settlement_id:
        settlement = session.get(Settlement, invoice.settlement_id)
    if purchase_request is None and settlement and settlement.purchase_request_id:
        purchase_request = session.get(PurchaseRequest, settlement.purchase_request_id)
    return InvoiceOut(
        invoice_id=invoice.invoice_id,
        number=getattr(invoice, 'number', None),
        invoice_name=getattr(invoice, 'number', None),
        issue_date=getattr(invoice, 'issue_date', None),
        seller_name=getattr(invoice, 'seller_name', None),
        seller_nip=getattr(invoice, 'seller_nip', None),
        net_total=getattr(invoice, 'net_total', None),
        vat_total=getattr(invoice, 'vat_total', None),
        status=invoice.status.value if getattr(invoice, 'status', None) else None,
        amount=(getattr(invoice, 'net_total', 0) or 0) + (getattr(invoice, 'vat_total', 0) or 0),
        created_at=getattr(invoice, 'created_at', None),
        project_finance_manager_id=getattr(invoice, 'project_finance_manager_id', None),
        project_finance_manager_name=_manager_name(
            getattr(invoice, 'project_finance_manager_id', None),
            session,
        ),
        settlement_id=getattr(invoice, 'settlement_id', None),
        purchase_request_id=settlement.purchase_request_id if settlement else None,
        purchase_request_name=(
            purchase_request.purchase_request_name if purchase_request else None
        ),
    )


@app.get("/api/settlements", response_model=List[SettlementOut])
def get_settlements_full(session: Session = Depends(get_session)):
    settlements = session.exec(select(Settlement)).all()
    return _enrich_settlements(settlements, session)


@app.get("/api/settlements/history", response_model=List[SettlementOut])
def get_settlements_history(session: Session = Depends(get_session)):
    settlements = session.exec(select(Settlement)).all()
    completed = []
    for settlement in settlements:
        if not settlement.purchase_request_id:
            continue
        purchase_request = session.get(PurchaseRequest, settlement.purchase_request_id)
        if purchase_request and purchase_request.finalization_status == "settled":
            completed.append(settlement)
    return _enrich_settlements(completed, session, active_only=False)


@app.get("/api/invoices", response_model=List[InvoiceOut])
def get_invoices(
    status: Optional[InvoiceStatus] = None,
    project_finance_manager_id: Optional[int] = None,
    purchase_request_id: Optional[int] = None,
    association_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    statement = select(Invoice)
    invoices = session.exec(statement).all()
    result: list[InvoiceOut] = []
    for invoice in invoices:
        settlement = (
            session.get(Settlement, invoice.settlement_id)
            if invoice.settlement_id
            else None
        )
        purchase_request = (
            session.get(PurchaseRequest, settlement.purchase_request_id)
            if settlement and settlement.purchase_request_id
            else None
        )
        if status is not None and invoice.status != status:
            continue
        if (
            project_finance_manager_id is not None
            and invoice.project_finance_manager_id != project_finance_manager_id
        ):
            continue
        if (
            purchase_request_id is not None
            and (not purchase_request or purchase_request.purchase_request_id != purchase_request_id)
        ):
            continue
        if association_id is not None:
            if not purchase_request:
                continue
            project_budget = session.get(ProjectBudget, purchase_request.project_budget_id)
            project = (
                session.get(Project, project_budget.project_id)
                if project_budget
                else None
            )
            if not project or project.association_id != association_id:
                continue
        result.append(_invoice_out(invoice, session, settlement, purchase_request))
    return result


@app.post("/api/settlements", response_model=SettlementOut)
def create_settlement(new_settlement_data: SettlementCreate, session: Session = Depends(get_session)):
    if new_settlement_data.purchase_request_id:
        purchase_request = session.get(PurchaseRequest, new_settlement_data.purchase_request_id)
        if not purchase_request:
            raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")

    if new_settlement_data.paid_by_project_finance_manager_id:
        project_finance_manager = session.get(
            ProjectFinanceManager,
            new_settlement_data.paid_by_project_finance_manager_id,
        )
        if not project_finance_manager:
            raise HTTPException(status_code=404, detail="Skarbnik nie znaleziony")

    settlement = Settlement(
        created_at=new_settlement_data.created_at,
        paid_by_project_finance_manager_id=new_settlement_data.paid_by_project_finance_manager_id,
        purchase_request_id=new_settlement_data.purchase_request_id,
    )
    session.add(settlement)
    session.commit()
    session.refresh(settlement)

    return _enrich_settlements([settlement], session)[0]


@app.get("/api/settlements/manager/{project_finance_manager_id}", response_model=List[SettlementOut])
def get_settlements_full_by_manager(
    project_finance_manager_id: int,
    session: Session = Depends(get_session)
):
    settlements = session.exec(
        select(Settlement).where(
            Settlement.paid_by_project_finance_manager_id == project_finance_manager_id
        )
    ).all()
    return _enrich_settlements(settlements, session)


@app.post("/api/settlements/{settlement_id}/invoices", response_model=SettlementOut)
def create_invoice_for_settlement(
    settlement_id: int,
    new_invoice_data: InvoiceCreate,
    session: Session = Depends(get_session),
):
    settlement = session.get(Settlement, settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Rozliczenie nie znalezione")
    if new_invoice_data.project_finance_manager_id:
        manager = session.get(
            ProjectFinanceManager,
            new_invoice_data.project_finance_manager_id,
        )
        if not manager:
            raise HTTPException(status_code=404, detail="Skarbnik faktury nie znaleziony")

    invoice = Invoice(
        number=new_invoice_data.number,
        issue_date=new_invoice_data.issue_date,
        seller_name=new_invoice_data.seller_name,
        seller_nip=new_invoice_data.seller_nip,
        net_total=new_invoice_data.net_total,
        vat_total=new_invoice_data.vat_total,
        status=new_invoice_data.status,
        created_at=datetime.now(),
        settlement_id=settlement_id,
        project_finance_manager_id=new_invoice_data.project_finance_manager_id,
    )
    session.add(invoice)
    session.commit()

    refreshed_settlement = session.get(Settlement, settlement_id)
    return _enrich_settlements([refreshed_settlement], session)[0]


@app.patch("/api/invoices/{invoice_id}", response_model=SettlementOut)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    session: Session = Depends(get_session),
):
    invoice = session.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Faktura nie znaleziona")

    for field, value in invoice_data.model_dump(exclude_unset=True).items():
        if field == "project_finance_manager_id" and value is not None:
            manager = session.get(ProjectFinanceManager, value)
            if not manager:
                raise HTTPException(status_code=404, detail="Skarbnik faktury nie znaleziony")
        setattr(invoice, field, value)
    session.add(invoice)
    session.commit()
    session.refresh(invoice)

    settlement = session.get(Settlement, invoice.settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Rozliczenie faktury nie znalezione")
    return _enrich_settlements([settlement], session)[0]


@app.post("/api/settlements/{settlement_id}/complete", response_model=SettlementOut)
def complete_settlement(
    settlement_id: int,
    session: Session = Depends(get_session),
):
    settlement = session.get(Settlement, settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Rozliczenie nie znalezione")
    if not settlement.purchase_request_id:
        raise HTTPException(status_code=400, detail="Rozliczenie nie jest powiazane z wnioskiem")

    purchase_request = session.get(PurchaseRequest, settlement.purchase_request_id)
    if not purchase_request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")

    lines = session.exec(
        select(PurchaseRequestSettlementLine).where(
            PurchaseRequestSettlementLine.purchase_request_id
            == purchase_request.purchase_request_id
        )
    ).all()
    if lines and any(line.invoice_id is None for line in lines):
        raise HTTPException(status_code=400, detail="Nie wszystkie pozycje maja przypisana fakture")

    purchase_request.finalization_status = "settled"
    session.add(purchase_request)
    session.commit()
    session.refresh(settlement)
    return _enrich_settlements([settlement], session, active_only=False)[0]


@app.patch("/api/settlements/{settlement_id}/status", response_model=SettlementOut)
def update_settlement_status(
    settlement_id: int,
    status_data: SettlementStatusUpdate,
    session: Session = Depends(get_session),
):
    if status_data.status not in ("settlement", "settled"):
        raise HTTPException(status_code=400, detail="Nieprawidlowy status rozliczenia")

    settlement = session.get(Settlement, settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Rozliczenie nie znalezione")
    if not settlement.purchase_request_id:
        raise HTTPException(status_code=400, detail="Rozliczenie nie jest powiazane z wnioskiem")

    purchase_request = session.get(PurchaseRequest, settlement.purchase_request_id)
    if not purchase_request:
        raise HTTPException(status_code=404, detail="Wniosek nie znaleziony")

    purchase_request.finalization_status = status_data.status
    session.add(purchase_request)
    session.commit()
    session.refresh(settlement)
    return _enrich_settlements(
        [settlement],
        session,
        active_only=status_data.status == "settlement",
    )[0]


def _enrich_settlements(settlements, session: Session, active_only: bool = True) -> List[SettlementOut]:
    result = []
    emitted_request_ids = set()
    for s in settlements:
        purchase_request = (
            session.get(PurchaseRequest, s.purchase_request_id) if s.purchase_request_id else None
        )
        if (
            active_only
            and purchase_request
            and purchase_request.finalization_status != "settlement"
        ):
            continue
        if s.purchase_request_id and s.purchase_request_id in emitted_request_ids:
            continue
        if s.purchase_request_id:
            emitted_request_ids.add(s.purchase_request_id)

        related_settlements = [s]
        if s.purchase_request_id:
            related_settlements = session.exec(
                select(Settlement).where(
                    Settlement.purchase_request_id == s.purchase_request_id
                )
            ).all()
        related_settlement_ids = [
            settlement.settlement_id
            for settlement in related_settlements
            if settlement.settlement_id
        ]

        invoices = []
        if related_settlement_ids:
            invoices = session.exec(
                select(Invoice).where(Invoice.settlement_id.in_(related_settlement_ids))
            ).all()

        shop_purchase_lists = []
        if related_settlement_ids:
            shop_purchase_lists = session.exec(
                select(ShopPurchaseList).where(
                    ShopPurchaseList.settlement_id.in_(related_settlement_ids)
                )
            ).all()

        settlement_lines = []
        if s.purchase_request_id:
            settlement_lines = session.exec(
                select(PurchaseRequestSettlementLine).where(
                    PurchaseRequestSettlementLine.purchase_request_id
                    == s.purchase_request_id
                )
            ).all()
        
        total_spent = (
            sum(float(line.actual_gross_amount or 0) for line in settlement_lines)
            if settlement_lines
            else sum(
                (getattr(i, 'net_total', 0) or 0) + (getattr(i, 'vat_total', 0) or 0)
                for i in invoices
            )
        )

        result.append(
            SettlementOut(
                settlement_id=s.settlement_id,
                created_at=s.created_at,
                paid_by_project_finance_manager_id=s.paid_by_project_finance_manager_id,
                purchase_request_id=s.purchase_request_id,
                purchase_request=(
                    PurchaseRequestOut.model_validate(purchase_request)
                    if purchase_request
                    else None
                ),
                invoices=[
                    _invoice_out(i, session, s, purchase_request)
                    for i in invoices
                ],
                shop_purchase_lists=[ShopPurchaseListOut.model_validate(sp) for sp in shop_purchase_lists],
                settlement_lines=[
                    SettlementLineOut(
                        settlement_line_id=line.settlement_line_id,
                        purchase_request_id=line.purchase_request_id,
                        shop_purchase_list_id=line.shop_purchase_list_id,
                        invoice_id=line.invoice_id,
                        invoice_number=(
                            session.get(Invoice, line.invoice_id).number
                            if line.invoice_id and session.get(Invoice, line.invoice_id)
                            else None
                        ),
                        shop_name=line.shop_name,
                        purchase_description=line.purchase_description,
                        planned_gross_amount=line.planned_gross_amount,
                        actual_gross_amount=line.actual_gross_amount,
                        difference_amount=(
                            float(line.planned_gross_amount or 0)
                            - float(line.actual_gross_amount or 0)
                        ),
                        is_extra=line.is_extra,
                    )
                    for line in settlement_lines
                ],
                total_spent=total_spent,
            )
        )

    return result
