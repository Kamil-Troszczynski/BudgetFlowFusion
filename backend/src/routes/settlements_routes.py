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


class PurchaseRequestOut(BaseModel):
    purchase_request_id: int
    purchase_request_name: Optional[str] = None
    budget_allocated_for_the_order: Optional[float] = None
    if_service: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class ShopPurchaseListOut(BaseModel):
    shop_purchase_list_id: int
    model_config = ConfigDict(from_attributes=True)


class SettlementOut(BaseModel):
    settlement_id: int
    created_at: datetime
    paid_by_project_finance_manager_id: Optional[int] = None
    purchase_request_id: Optional[int] = None
    purchase_request: Optional[PurchaseRequestOut] = None
    invoices: List[InvoiceOut] = []
    shop_purchase_lists: List[ShopPurchaseListOut] = []
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


@app.get("/api/settlements", response_model=List[SettlementOut])
def get_settlements_full(session: Session = Depends(get_session)):
    settlements = session.exec(select(Settlement)).all()
    return _enrich_settlements(settlements, session)


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
    )
    session.add(invoice)
    session.commit()

    refreshed_settlement = session.get(Settlement, settlement_id)
    return _enrich_settlements([refreshed_settlement], session)[0]


def _enrich_settlements(settlements, session: Session) -> List[SettlementOut]:
    result = []
    for s in settlements:
        purchase_request = (
            session.get(PurchaseRequest, s.purchase_request_id) if s.purchase_request_id else None
        )

        invoices = session.exec(
            select(Invoice).where(Invoice.settlement_id == s.settlement_id)
        ).all()

        shop_purchase_lists = session.exec(
            select(ShopPurchaseList).where(
                ShopPurchaseList.settlement_id == s.settlement_id
            )
        ).all()
        
        total_spent = sum(
            (getattr(i, 'net_total', 0) or 0) + (getattr(i, 'vat_total', 0) or 0)
            for i in invoices
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
                    InvoiceOut(
                        invoice_id=i.invoice_id,
                        number=getattr(i, 'number', None),
                        invoice_name=getattr(i, 'number', None),
                        issue_date=getattr(i, 'issue_date', None),
                        seller_name=getattr(i, 'seller_name', None),
                        seller_nip=getattr(i, 'seller_nip', None),
                        net_total=getattr(i, 'net_total', None),
                        vat_total=getattr(i, 'vat_total', None),
                        status=i.status.value if getattr(i, 'status', None) else None,
                        amount=(getattr(i, 'net_total', 0) or 0) + (getattr(i, 'vat_total', 0) or 0),
                        created_at=getattr(i, 'created_at', None)
                    ) for i in invoices
                ],
                shop_purchase_lists=[ShopPurchaseListOut.model_validate(sp) for sp in shop_purchase_lists],
                total_spent=total_spent,
            )
        )

    return result
