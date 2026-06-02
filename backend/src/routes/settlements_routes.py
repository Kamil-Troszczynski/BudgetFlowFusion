from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class InvoiceOut(BaseModel):
    invoice_id: int
    invoice_name: Optional[str] = None
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


@app.get("/api/settlements", response_model=List[SettlementOut])
def get_settlements_full(session: Session = Depends(get_session)):
    settlements = session.exec(select(Settlement)).all()
    return _enrich_settlements(settlements, session)


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
                        invoice_name=getattr(i, 'number', None), 
                        amount=(getattr(i, 'net_total', 0) or 0) + (getattr(i, 'vat_total', 0) or 0), 
                        created_at=getattr(i, 'created_at', None)
                    ) for i in invoices
                ],
                shop_purchase_lists=[ShopPurchaseListOut.model_validate(sp) for sp in shop_purchase_lists],
                total_spent=total_spent,
            )
        )

    return result