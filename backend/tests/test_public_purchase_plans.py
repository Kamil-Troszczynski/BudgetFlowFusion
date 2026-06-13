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
        association_budget_id=budget.association_budget_id,
    )
    other_funding = Funding(
        funding_name="Obce dofinansowanie",
        funding_price=2000.0,
        spent_money=0.0,
        project_id=other_project.project_id,
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
    assert data[0]["available_money"] == 17500.0
    assert len(data[0]["fundings"]) == 1
    assert data[0]["fundings"][0]["funding_name"] == "Grant testowy"
    assert data[0]["fundings"][0]["available_money"] == 6500.0


def test_create_public_purchase_plan_list_attaches_to_budget(client, session, public_plan_seed):
    budget = public_plan_seed["budget"]

    response = client.post(
        "/api/public_purchase_plan_lists",
        json={
            "association_budget_id": budget.association_budget_id,
            "public_plan_list_name": "Plan zamówień publicznych 2026",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["public_plan_list_name"] == "Plan zamówień publicznych 2026"

    session.refresh(budget)
    attached_list = session.get(PublicPurchasePlanList, budget.public_purchase_plan_list_id)
    assert attached_list is not None
    assert attached_list.public_plan_list_name == "Plan zamówień publicznych 2026"


def test_create_public_purchase_plan_with_budget_funding(client, session, public_plan_seed):
    budget = public_plan_seed["budget"]
    funding = public_plan_seed["funding"]
    plan_list = PublicPurchasePlanList(public_plan_list_name="Lista testowa")
    session.add(plan_list)
    session.commit()
    session.refresh(plan_list)

    budget.public_purchase_plan_list_id = plan_list.public_purchase_plan_list_id
    session.add(budget)
    session.commit()

    response = client.post(
        "/api/public_purchase_plans",
        json={
            "public_purchase_plan_list_id": plan_list.public_purchase_plan_list_id,
            "public_purchase_plan_name": "Zakup podzespołów",
            "cost": 1200.0,
            "funding_id": funding.funding_id,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["public_purchase_plan_name"] == "Zakup podzespołów"
    assert data["funding_name"] == "Grant testowy"

    db_plan = session.exec(
        select(PublicPurchasePlan).where(
            PublicPurchasePlan.public_purchase_plan_name == "Zakup podzespołów"
        )
    ).first()
    assert db_plan is not None
    assert db_plan.funding_id == funding.funding_id


def test_create_public_purchase_plan_rejects_foreign_funding(client, session, public_plan_seed):
    budget = public_plan_seed["budget"]
    other_funding = public_plan_seed["other_funding"]
    plan_list = PublicPurchasePlanList(public_plan_list_name="Lista testowa")
    session.add(plan_list)
    session.commit()
    session.refresh(plan_list)

    budget.public_purchase_plan_list_id = plan_list.public_purchase_plan_list_id
    session.add(budget)
    session.commit()

    response = client.post(
        "/api/public_purchase_plans",
        json={
            "public_purchase_plan_list_id": plan_list.public_purchase_plan_list_id,
            "public_purchase_plan_name": "Niepoprawny zakup",
            "cost": 100.0,
            "funding_id": other_funding.funding_id,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Dofinansowanie nie należy do wskazanego budżetu koła"
