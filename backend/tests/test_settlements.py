import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timezone
from src import app, get_session
from src.relations import Settlement, PurchaseRequest, Invoice, ShopPurchaseList


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
    pr = PurchaseRequest(
        purchase_request_id=1,
        purchase_request_name="Zakup licencji",
        budget_allocated_for_the_order=5000.0,
        if_service=True,
        used_cpv_id=101,  
        association_budget_id=1,
        created_at=datetime.now(timezone.utc),
        can_add=True,
        project_finance_manager_id=10
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
        status="paid",  
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
        status="paid", 
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