import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timezone
from src import app, get_session
from src.relations import AssociationBudget, Project, ProjectBudget, PurchaseRequest


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
    budget = AssociationBudget(
        association_budget_id=1,
        association_budget_name="Budżet testowy",
        total_budget=50000.0,
        spent_money=0.0,
    )
    project = Project(
        project_id=1,
        project_name="Projekt testowy",
        description="Test",
        allocated_budget=50000.0,
        rest_of_budget=50000.0,
    )
    session.add_all([budget, project])
    session.commit()
    project_budget = ProjectBudget(
        project_budget_id=1,
        project_budget_name="Budżet projektu testowego",
        total_budget=50000.0,
        spent_money=0.0,
        association_budget_id=1,
        project_id=1,
    )
    session.add(project_budget)
    session.commit()

    pr1 = PurchaseRequest(
        purchase_request_id=1,
        purchase_request_name="Zakup sprzętu IT",
        budget_allocated_for_the_order=15000.0,
        if_service=False,
        used_cpv_id=101,
        project_budget_id=1,
        created_at=datetime.now(timezone.utc),
        can_add=True,
        project_finance_manager_id=10
    )
    
    pr2 = PurchaseRequest(
        purchase_request_id=2,
        purchase_request_name="Usługi prawne",
        budget_allocated_for_the_order=5000.0,
        if_service=True,
        used_cpv_id=202,
        project_budget_id=1,
        created_at=datetime.now(timezone.utc),
        can_add=False,
        project_finance_manager_id=20
    )
    
    session.add(pr1)
    session.add(pr2)
    session.commit()


def test_get_all_purchase_requests(client: TestClient, seed_data):
    response = client.get("/api/purchase_requests")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["purchase_request_name"] == "Zakup sprzętu IT"
    assert data[1]["purchase_request_name"] == "Usługi prawne"


def test_get_single_purchase_request(client: TestClient, seed_data):
    response = client.get("/api/purchase_requests/detail/1")
    assert response.status_code == 200
    
    data = response.json()
    assert data["purchase_request_id"] == 1
    assert data["budget_allocated_for_the_order"] == 15000.0
    assert data["if_service"] is False


def test_get_single_purchase_request_not_found(client: TestClient, seed_data):
    response = client.get("/api/purchase_requests/detail/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Wniosek nie znaleziony"


def test_get_requests_by_project_finance_manager(client: TestClient, seed_data):
    response = client.get("/api/purchase_requests/20")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["purchase_request_id"] == 2
    assert data[0]["project_finance_manager_id"] == 20


def test_create_purchase_request(client: TestClient, session: Session):
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
    )
    session.add_all([budget, project])
    session.commit()
    session.add(ProjectBudget(
        project_budget_id=1,
        project_budget_name="Budżet projektu testowego",
        total_budget=10000.0,
        spent_money=0.0,
        association_budget_id=1,
        project_id=1,
    ))
    session.commit()

    new_request_payload = {
        "purchase_request_name": "Nowe biurka",
        "budget_allocated_for_the_order": 3000.50,
        "if_service": False,
        "used_cpv_id": 303,
        "project_budget_id": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "can_add": True,
        "project_finance_manager_id": 30
    }
    
    response = client.post("/api/create_purchase_requests", json=new_request_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["purchase_request_name"] == "Nowe biurka"
    assert data["budget_allocated_for_the_order"] == 3000.50
    assert "purchase_request_id" in data
    db_request = session.get(PurchaseRequest, data["purchase_request_id"])
    assert db_request is not None
    assert db_request.project_finance_manager_id == 30

    budgets_response = client.get("/api/project_budgets")
    assert budgets_response.status_code == 200
    project_budget = budgets_response.json()[0]
    assert project_budget["purchase_requests_total_allocated"] == 3000.50
    assert project_budget["available_after_purchase_requests"] == 6999.50


def test_delete_purchase_request(client: TestClient, session: Session, seed_data):
    response = client.delete("/api/purchase_requests/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Wniosek usunięty pomyślnie"
    db_request = session.get(PurchaseRequest, 1)
    assert db_request is None
    get_response = client.get("/api/purchase_requests/detail/1")
    assert get_response.status_code == 404


def test_delete_purchase_request_not_found(client: TestClient, seed_data):
    response = client.delete("/api/purchase_requests/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Wniosek nie znaleziony"
