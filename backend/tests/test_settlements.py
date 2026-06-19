import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timezone
from src import app, get_session
from src.relations import (
    Association,
    AssociationBudget,
    Funding,
    Invoice,
    InvoiceStatus,
    Project,
    ProjectBudget,
    PurchaseRequest,
    PurchaseRequestSettlementLine,
    Settlement,
    Shop,
    ShopPurchaseList,
    Student,
)


sqlite_url = "sqlite://"
engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="seed_data")
def seed_data_fixture(session: Session):
    association = Association(
        association_id=1,
        association_name="Koło testowe",
    )
    budget = AssociationBudget(
        association_budget_id=1,
        association_budget_name="Budżet testowy",
        total_budget=10000.0,
        spent_money=0.0,
    )
    project = Project(
        project_id=1,
        project_name="Projekt testowy",
        description="Test",
        allocated_budget=10000.0,
        rest_of_budget=10000.0,
        association_id=1,
    )
    session.add_all([association, budget, project])
    session.commit()
    project_budget = ProjectBudget(
        project_budget_id=1,
        project_budget_name="Budżet projektu testowego",
        total_budget=10000.0,
        spent_money=0.0,
        association_budget_id=1,
        project_id=1,
    )
    funding = Funding(
        funding_id=1,
        funding_name="Dofinansowanie testowe",
        funding_price=10000.0,
        spent_money=0.0,
        project_id=1,
        project_budget_id=1,
        association_budget_id=1,
    )
    shop = Shop(
        shop_id=1,
        shop_name="Sklep testowy",
        address="Online",
        delivery_time=datetime.now(timezone.utc),
        is_recommended=True,
        free_delivery_threshold=100.0,
    )
    student = Student(
        student_id=1,
        name="Jan",
        surname="Testowy",
        login="jan@test.pl",
        password_hash="hash",
        position="member",
        is_in_sap=True,
        association_id=1,
    )
    session.add_all([project_budget, funding, shop, student])
    session.commit()

    pr = PurchaseRequest(
        purchase_request_id=1,
        purchase_request_name="Zakup licencji",
        budget_allocated_for_the_order=5000.0,
        if_service=True,
        used_cpv_id="101",
        project_budget_id=1,
        funding_id=1,
        created_at=datetime.now(timezone.utc),
        can_add=True,
        project_finance_manager_id=10,
        finalization_status="settlement",
    )
    session.add(pr)

    settlement1 = Settlement(
        settlement_id=1,
        created_at=datetime.now(timezone.utc),
        paid_by_project_finance_manager_id=10,
        purchase_request_id=1
    )
    
    settlement2 = Settlement(
        settlement_id=2,
        created_at=datetime.now(timezone.utc),
        paid_by_project_finance_manager_id=20,
        purchase_request_id=None
    )
    session.add(settlement1)
    session.add(settlement2)

    invoice1 = Invoice(
        invoice_id=101,
        number="FAV/01/2023",
        issue_date=datetime.now(timezone.utc).date(),
        seller_name="TechCorp",
        seller_nip="1234567890",
        net_total=1000.0,
        vat_total=230.0,
        status=InvoiceStatus.paid,
        created_at=datetime.now(timezone.utc),
        settlement_id=1
    )
    invoice2 = Invoice(
        invoice_id=102,
        number="FAV/02/2023",
        issue_date=datetime.now(timezone.utc).date(),
        seller_name="OfficeSupplies",
        seller_nip="0987654321",
        net_total=500.0,
        vat_total=115.0,
        status=InvoiceStatus.paid,
        created_at=datetime.now(timezone.utc),
        settlement_id=1
    )
    session.add(invoice1)
    session.add(invoice2)

    spl = ShopPurchaseList(
        shop_purchase_list_id=999,
        settlement_id=1,
        priority=1,            
        name="Testowy zakup",  
        cost=150.0,           
        created_at=datetime.now(timezone.utc),
        funding_id=1,
        shop_id=1,
        gslbccf_id=1,
        student_id=1
    )
    session.add(spl)
    session.commit()



def test_get_all_settlements(client: TestClient, seed_data):
    response = client.get("/api/settlements")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    s1 = next(item for item in data if item["settlement_id"] == 1)

    assert s1["total_spent"] == 1845.0
    assert len(s1["invoices"]) == 2
    assert s1["invoices"][0]["invoice_name"] == "FAV/01/2023"
    assert s1["invoices"][0]["amount"] == 1230.0
    assert s1["purchase_request"] is not None
    assert s1["purchase_request"]["purchase_request_name"] == "Zakup licencji"


def test_get_settlements_by_manager(client: TestClient, seed_data):
    response = client.get("/api/settlements/manager/10")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["settlement_id"] == 1
    assert data[0]["paid_by_project_finance_manager_id"] == 10


def test_get_settlements_by_manager_empty(client: TestClient, seed_data):
    response = client.get("/api/settlements/manager/999")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_complete_settlement_rejects_line_without_invoice(client: TestClient, session: Session, seed_data):
    line = PurchaseRequestSettlementLine(
        purchase_request_id=1,
        shop_purchase_list_id=999,
        invoice_id=None,
        shop_name="Sklep testowy",
        purchase_description="Pozycja bez faktury",
        planned_gross_amount=100.0,
        actual_gross_amount=100.0,
        is_extra=False,
        created_at=datetime.now(timezone.utc),
    )
    session.add(line)
    session.commit()

    response = client.post("/api/settlements/1/complete")

    assert response.status_code == 400
    assert response.json()["detail"] == "Nie wszystkie pozycje maja przypisana fakture"


def test_update_settlement_status_marks_request_as_settled(client: TestClient, session: Session, seed_data):
    response = client.patch("/api/settlements/1/status", json={"status": "settled"})

    assert response.status_code == 200
    request = session.get(PurchaseRequest, 1)
    assert request.finalization_status == "settled"
