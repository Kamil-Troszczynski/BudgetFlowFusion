import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from datetime import datetime
from src import app, get_session
from src.relations import *


DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
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

@pytest.fixture(name="mock_db")
def mock_db_data(session: Session):
    """
    Funkcja przygotowująca niezbędne relacje (klucze obce),
    aby można było testować dodawanie przedmiotów.
    """
    assoc = Association(association_name="Koło Testowe")
    session.add(assoc)
    session.commit()

    normal_student = Student(
        name="Jan", surname="Zwykły", login="jan@edu.pl",
        password_hash="123", position="member", is_in_sap=False,
        association_id=assoc.association_id
    )

    finance_manager = ProjectFinanceManager(login="skarbnik@edu.pl", password_hash="123", access=True)
    session.add(finance_manager)
    session.commit()

    treasurer = Student(
        name="Anna", surname="Skarbnik", login="anna@edu.pl",
        password_hash="123", position="treasurer", is_in_sap=True,
        association_id=assoc.association_id,
        project_finance_manager_id=finance_manager.project_finance_manager_id
    )

    shop = Shop(shop_name="Sklep Test", address="Online", delivery_time=datetime.now(), is_recommended=True, free_delivery_threshold=100)

    cat = ProductCategory(product_category_name="Elektronika", description="Test", cpv="31700000-3")
    session.add(cat)
    session.commit()

    subcat = ProductSubcategory(product_subcategory_name="Czujniki", description="Test", product_category_id=cat.product_category_id)

    session.add_all([normal_student, treasurer, shop, subcat])
    session.commit()

    return {
        "normal_student": normal_student,
        "treasurer": treasurer,
        "shop": shop,
        "subcat": subcat,
        "association": assoc
    }