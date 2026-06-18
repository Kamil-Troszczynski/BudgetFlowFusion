import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from datetime import datetime, timezone
from src import app, get_session
from src.relations import (
    Association,
    AssociationBudget,
    Funding,
    Project,
    ProjectBudget,
    PurchaseRequestFundingAllocation,
    PurchaseRequestPlanPosition,
    PublicPurchasePlan,
    PublicPurchasePlanList,
    PurchaseRequest,
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


def create_budget_graph(session: Session):
    association = Association(association_id=1, association_name="Koło testowe")
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
    session.add(project_budget)
    session.commit()
    funding = Funding(
        funding_id=1,
        funding_name="Dofinansowanie testowe",
        funding_price=10000.0,
        spent_money=0.0,
        project_id=1,
        project_budget_id=1,
        association_budget_id=1,
    )
    session.add(funding)
    session.commit()
    return association, budget, project, project_budget, funding


def create_plan(session: Session, funding_id: int = 1, cpv_code: str = "30300000", cost: float = 5000.0):
    plan_list = PublicPurchasePlanList(
        public_plan_list_name="Plan testowy",
        plan_year=2026,
        funding_id=funding_id,
    )
    session.add(plan_list)
    session.commit()
    session.refresh(plan_list)
    plan_position = PublicPurchasePlan(
        public_purchase_plan_name=f"CPV {cpv_code}",
        cpv_code=cpv_code,
        cost=cost,
        funding_id=funding_id,
        public_purchase_plan_list_id=plan_list.public_purchase_plan_list_id,
    )
    session.add(plan_position)
    session.commit()
    session.refresh(plan_position)
    return plan_list, plan_position


@pytest.fixture(name="seed_data")
def seed_data_fixture(session: Session):
    create_budget_graph(session)

    pr1 = PurchaseRequest(
        purchase_request_id=1,
        purchase_request_name="Zakup sprzętu IT",
        budget_allocated_for_the_order=15000.0,
        if_service=False,
        used_cpv_id="101",
        project_budget_id=1,
        funding_id=1,
        created_at=datetime.now(timezone.utc),
        can_add=True,
        project_finance_manager_id=10
    )
    
    pr2 = PurchaseRequest(
        purchase_request_id=2,
        purchase_request_name="Usługi prawne",
        budget_allocated_for_the_order=5000.0,
        if_service=True,
        used_cpv_id="202",
        project_budget_id=1,
        funding_id=1,
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
    create_budget_graph(session)
    _, plan_position = create_plan(session)

    new_request_payload = {
        "purchase_request_name": "Nowe biurka",
        "budget_allocated_for_the_order": 3000.50,
        "if_service": False,
        "used_cpv_id": "30300000",
        "project_budget_id": 1,
        "funding_id": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "can_add": True,
        "project_finance_manager_id": 30,
        "public_purchase_plan_id": plan_position.public_purchase_plan_id,
    }
    
    response = client.post("/api/create_purchase_requests", json=new_request_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["purchase_request_name"] == "Nowe biurka"
    assert data["budget_allocated_for_the_order"] == 3000.50
    assert data["plan_compliance_status"] == "compliant"
    assert data["used_cpv_id"] == "30300000"
    assert data["plan_position"]["remaining_amount"] == 1999.50
    assert "purchase_request_id" in data
    db_request = session.get(PurchaseRequest, data["purchase_request_id"])
    assert db_request is not None
    assert db_request.project_finance_manager_id == 30

    budgets_response = client.get("/api/project_budgets")
    assert budgets_response.status_code == 200
    project_budget = budgets_response.json()[0]
    assert project_budget["purchase_requests_total_allocated"] == 3000.50
    assert project_budget["available_after_purchase_requests"] == 6999.50

    fundings_response = client.get("/api/fundings")
    assert fundings_response.status_code == 200
    funding = fundings_response.json()[0]
    assert funding["purchase_requests_total_allocated"] == 3000.50
    assert funding["available_after_purchase_requests"] == 6999.50


def test_create_purchase_request_rejects_plan_overrun_without_justification(client: TestClient, session: Session):
    create_budget_graph(session)
    _, plan_position = create_plan(session, cost=1000.0)

    response = client.post(
        "/api/create_purchase_requests",
        json={
            "purchase_request_name": "Za drogi zakup",
            "budget_allocated_for_the_order": 1500.0,
            "if_service": False,
            "used_cpv_id": "30300000",
            "project_budget_id": 1,
            "funding_id": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "can_add": True,
            "project_finance_manager_id": 30,
            "public_purchase_plan_id": plan_position.public_purchase_plan_id,
        },
    )

    assert response.status_code == 400
    assert "Uzasadnienie odstępstwa jest wymagane" in response.json()["detail"]


def test_create_purchase_request_allows_plan_overrun_with_justification(client: TestClient, session: Session):
    create_budget_graph(session)
    _, plan_position = create_plan(session, cost=1000.0)

    response = client.post(
        "/api/create_purchase_requests",
        json={
            "purchase_request_name": "Zakup z odstępstwem",
            "budget_allocated_for_the_order": 1500.0,
            "if_service": False,
            "used_cpv_id": "30300000",
            "project_budget_id": 1,
            "funding_id": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "can_add": True,
            "project_finance_manager_id": 30,
            "public_purchase_plan_id": plan_position.public_purchase_plan_id,
            "plan_exception_justification": "Cena wzrosła po złożeniu planu.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["plan_compliance_status"] == "requires_approval"
    assert data["plan_exception_justification"] == "Cena wzrosła po złożeniu planu."
    assert data["plan_position"]["remaining_amount"] == -500.0


def test_create_purchase_request_stores_funding_allocations(client: TestClient, session: Session):
    create_budget_graph(session)
    second_funding = Funding(
        funding_id=2,
        funding_name="Drugie dofinansowanie",
        funding_price=7000.0,
        spent_money=0.0,
        project_id=1,
        project_budget_id=1,
        association_budget_id=1,
    )
    session.add(second_funding)
    session.commit()

    response = client.post(
        "/api/create_purchase_requests",
        json={
            "purchase_request_name": "Zakup z dwóch źródeł",
            "budget_allocated_for_the_order": 3000.0,
            "if_service": False,
            "used_cpv_id": "31700000",
            "project_budget_id": 1,
            "funding_id": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "can_add": True,
            "project_finance_manager_id": 30,
            "funding_allocations": [
                {"funding_id": 1, "allocated_amount": 1000.0},
                {"funding_id": 2, "allocated_amount": 2000.0},
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["plan_compliance_status"] == "draft"
    assert len(data["funding_allocations"]) == 2
    assert sum(row["allocated_amount"] for row in data["funding_allocations"]) == 3000.0

    rows = session.exec(select(PurchaseRequestFundingAllocation)).all()
    assert len(rows) == 2


def test_create_purchase_request_stores_plan_positions_when_shop_list_is_provided(client: TestClient, session: Session):
    create_budget_graph(session)
    _, plan_position = create_plan(session, cost=5000.0)
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
    purchase_list = ShopPurchaseList(
        shop_purchase_list_id=1,
        priority=1,
        name="Koszyk testowy",
        cost=1200.0,
        created_at=datetime.now(timezone.utc),
        funding_id=1,
        shop_id=1,
        student_id=1,
    )
    session.add_all([shop, student, purchase_list])
    session.commit()

    response = client.post(
        "/api/create_purchase_requests",
        json={
            "purchase_request_name": "Wniosek z pozycją koszyka",
            "budget_allocated_for_the_order": 1200.0,
            "if_service": False,
            "used_cpv_id": "30300000",
            "project_budget_id": 1,
            "funding_id": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "can_add": True,
            "project_finance_manager_id": 30,
            "plan_positions": [
                {
                    "shop_purchase_list_id": 1,
                    "public_purchase_plan_id": plan_position.public_purchase_plan_id,
                    "allocated_amount": 1200.0,
                }
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["plan_positions"]) == 1
    assert data["plan_positions"][0]["allocated_amount"] == 1200.0

    rows = session.exec(select(PurchaseRequestPlanPosition)).all()
    assert len(rows) == 1
    assert rows[0].shop_purchase_list_id == 1


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
