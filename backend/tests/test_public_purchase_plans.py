import pytest
from sqlmodel import Session, select
from src.relations import (
    Association,
    AssociationBudget,
    Funding,
    Project,
    ProjectBudget,
    PublicPurchasePlan,
    PublicPurchasePlanList,
)


@pytest.fixture(name="public_plan_seed")
def public_plan_seed_fixture(session: Session):
    association = Association(association_name="Koło Planów Publicznych")
    other_association = Association(association_name="Obce Koło")
    session.add_all([association, other_association])
    session.commit()
    session.refresh(association)
    session.refresh(other_association)

    project = Project(
        project_name="Projekt główny",
        description="Projekt testowy",
        allocated_budget=10000.0,
        rest_of_budget=10000.0,
        association_id=association.association_id,
    )
    other_project = Project(
        project_name="Projekt obcy",
        description="Projekt innego koła",
        allocated_budget=5000.0,
        rest_of_budget=5000.0,
        association_id=other_association.association_id,
    )
    session.add_all([project, other_project])
    session.commit()
    session.refresh(project)
    session.refresh(other_project)

    budget = AssociationBudget(
        association_budget_name="Budżet testowy",
        total_budget=20000.0,
        spent_money=2500.0,
    )
    other_budget = AssociationBudget(
        association_budget_name="Budżet obcy",
        total_budget=5000.0,
        spent_money=0.0,
    )
    session.add_all([budget, other_budget])
    session.commit()
    session.refresh(budget)
    session.refresh(other_budget)

    project_budget = ProjectBudget(
        project_budget_name="Budżet projektu głównego",
        total_budget=10000.0,
        spent_money=0.0,
        association_budget_id=budget.association_budget_id,
        project_id=project.project_id,
    )
    other_project_budget = ProjectBudget(
        project_budget_name="Budżet projektu obcego",
        total_budget=5000.0,
        spent_money=0.0,
        association_budget_id=other_budget.association_budget_id,
        project_id=other_project.project_id,
    )
    session.add_all([project_budget, other_project_budget])
    session.commit()

    funding = Funding(
        funding_name="Grant testowy",
        funding_price=8000.0,
        spent_money=1500.0,
        project_id=project.project_id,
        project_budget_id=project_budget.project_budget_id,
        association_budget_id=budget.association_budget_id,
    )
    other_funding = Funding(
        funding_name="Obce dofinansowanie",
        funding_price=2000.0,
        spent_money=0.0,
        project_id=other_project.project_id,
        project_budget_id=other_project_budget.project_budget_id,
        association_budget_id=other_budget.association_budget_id,
    )
    session.add_all([funding, other_funding])
    session.commit()
    session.refresh(funding)
    session.refresh(other_funding)

    return {
        "association": association,
        "budget": budget,
        "funding": funding,
        "project_budget": project_budget,
        "other_funding": other_funding,
    }


def test_get_association_budgets_with_fundings(client, public_plan_seed):
    association_id = public_plan_seed["association"].association_id

    response = client.get(f"/api/association_budgets?association_id={association_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["association_budget_name"] == "Budżet testowy"
    assert data[0]["total_budget"] == 8000.0
    assert data[0]["spent_money"] == 1500.0
    assert data[0]["available_money"] == 6500.0
    assert len(data[0]["fundings"]) == 1
    assert data[0]["fundings"][0]["funding_name"] == "Grant testowy"
    assert data[0]["fundings"][0]["available_money"] == 6500.0
    assert data[0]["fundings"][0]["project_budget_id"] == public_plan_seed["project_budget"].project_budget_id


def test_funding_is_assigned_to_one_section_budget(client, public_plan_seed):
    association_id = public_plan_seed["association"].association_id

    response = client.get(f"/api/fundings?association_id={association_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["funding_name"] == "Grant testowy"
    assert data[0]["project_budget_name"] == "Budżet projektu głównego"


def test_dashboard_budget_is_sum_of_section_fundings(client, public_plan_seed):
    association_id = public_plan_seed["association"].association_id

    response = client.get(
        f"/api/dashboard/budget_summary?association_id={association_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_budget"] == 8000.0
    assert data["spent_money"] == 1500.0
    assert data["available_after_purchase_requests"] == 6500.0


def test_create_public_purchase_plan_list_for_funding(client, session, public_plan_seed):
    funding = public_plan_seed["funding"]

    response = client.post(
        "/api/public_purchase_plan_lists",
        json={
            "funding_id": funding.funding_id,
            "public_plan_list_name": "Plan zamówień publicznych 2026",
            "plan_year": 2026,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["public_plan_list_name"] == "Plan zamówień publicznych 2026"
    assert data["funding_id"] == funding.funding_id
    assert data["plan_year"] == 2026


def test_create_public_purchase_plan_position(client, session, public_plan_seed):
    funding = public_plan_seed["funding"]
    plan_list = PublicPurchasePlanList(
        public_plan_list_name="Lista testowa",
        plan_year=2026,
        funding_id=funding.funding_id,
    )
    session.add(plan_list)
    session.commit()
    session.refresh(plan_list)

    response = client.post(
        "/api/public_purchase_plans",
        json={
            "public_purchase_plan_list_id": plan_list.public_purchase_plan_list_id,
            "cpv_code": 42000000,
            "cost": 1200.0,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["cpv_code"] == 42000000
    assert data["funding_id"] == funding.funding_id
    assert data["remaining_amount"] == 1200.0

    db_plan = session.exec(
        select(PublicPurchasePlan).where(
            PublicPurchasePlan.cpv_code == 42000000
        )
    ).first()
    assert db_plan is not None
    assert db_plan.funding_id == funding.funding_id


def test_create_public_purchase_plan_rejects_duplicate_cpv(client, session, public_plan_seed):
    funding = public_plan_seed["funding"]
    plan_list = PublicPurchasePlanList(
        public_plan_list_name="Lista testowa",
        plan_year=2026,
        funding_id=funding.funding_id,
    )
    session.add(plan_list)
    session.commit()
    session.refresh(plan_list)
    session.add(PublicPurchasePlan(
        public_purchase_plan_name="CPV 42000000",
        cpv_code=42000000,
        cost=1000.0,
        funding_id=funding.funding_id,
        public_purchase_plan_list_id=plan_list.public_purchase_plan_list_id,
    ))
    session.commit()

    response = client.post(
        "/api/public_purchase_plans",
        json={
            "public_purchase_plan_list_id": plan_list.public_purchase_plan_list_id,
            "cpv_code": 42000000,
            "cost": 100.0,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Ten kod CPV już istnieje w planie dofinansowania"
