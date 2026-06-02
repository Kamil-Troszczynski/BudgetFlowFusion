import pytest
from src.relations import Item, ProductSubcategory, Association, Student
from datetime import datetime
from sqlmodel import select


def test_add_category_and_subcategory(client, session):
    """Test sprawdza, czy kody CPV i kategorie poprawnie zapisują się w bazie"""
    response_cat = client.post("/api/categories", json={
        "name": "Narzędzia",
        "cpv": "43800000-1"
    })
    assert response_cat.status_code == 200
    cat_data = response_cat.json()
    assert cat_data["product_category_name"] == "Narzędzia"

    response_sub = client.post("/api/subcategories", json={
        "name": "Wiertarki",
        "product_category_id": cat_data["product_category_id"]
    })
    assert response_sub.status_code == 200

    db_subcat = session.exec(select(ProductSubcategory).where(ProductSubcategory.product_subcategory_name == "Wiertarki")).first()
    assert db_subcat is not None
    assert db_subcat.product_category_id == cat_data["product_category_id"]

def test_normal_student_adds_item_is_pending(client, session, mock_db):
    """Test: Przedmiot dodany przez zwykłego studenta musi czekać na akceptację (pending)"""
    payload = {
        "name": "Bateria testowa",
        "link": "https://test.pl",
        "price": 50.0,
        "currency": "PLN",
        "product_subcategory_id": mock_db["subcat"].product_subcategory_id,
        "student_id": mock_db["normal_student"].student_id
    }

    response = client.post("/api/items", json=payload)
    assert response.status_code == 200

    item_data = response.json()
    assert item_data["status"] == "pending"

def test_treasurer_adds_item_is_approved(client, session, mock_db):
    """Test (Fast-Track): Przedmiot dodany przez Skarbnika jest z automatu zaakceptowany"""
    payload = {
        "name": "Silnik testowy",
        "link": "https://test.pl",
        "price": 100.0,
        "currency": "PLN",
        "product_subcategory_id": mock_db["subcat"].product_subcategory_id,
        "student_id": mock_db["treasurer"].student_id
    }

    response = client.post("/api/items", json=payload)
    assert response.status_code == 200

    item_data = response.json()
    assert item_data["status"] == "approved"

def test_multitenancy_isolation_for_treasurer(client, session, mock_db):
    """Test: Skarbnik nie widzi przedmiotów z innego Koła Naukowego"""
    other_assoc = Association(association_name="Obce Koło")
    session.add(other_assoc)
    session.commit()

    foreign_student = Student(
        name="Piotr", surname="Obcy", login="piotr@obce.pl",
        password_hash="123", position="member", is_in_sap=False,
        association_id=other_assoc.association_id
    )
    session.add(foreign_student)
    session.commit()

    item = Item(
        name="Obcy przedmiot", price=10.0, currency="PLN", status="pending",
        product_subcategory_id=mock_db["subcat"].product_subcategory_id,
        student_id=foreign_student.student_id,
        shop_id=mock_db["shop"].shop_id,
        created_at=datetime.now()
    )
    session.add(item)
    session.commit()

    my_association_id = mock_db["treasurer"].association_id
    response = client.get(f"/api/items/pending?association_id={my_association_id}")

    assert response.status_code == 200
    assert len(response.json()) == 0

def test_treasurer_approve_item_endpoint(client, session, mock_db):
    """Test: Weryfikacja czy endpoint PATCH poprawnie zmienia status na 'approved'"""
    item = Item(
        name="Silnik krokowy (do akceptacji)", price=45.0, currency="PLN", status="pending",
        product_subcategory_id=mock_db["subcat"].product_subcategory_id,
        student_id=mock_db["normal_student"].student_id,
        shop_id=mock_db["shop"].shop_id,
        created_at=datetime.now()
    )
    session.add(item)
    session.commit()

    response = client.patch(f"/api/items/{item.item_id}/approve")
    assert response.status_code == 200

    session.refresh(item)
    assert item.status == "approved"

def test_treasurer_reject_item_endpoint(client, session, mock_db):
    """Test: Weryfikacja czy endpoint DELETE poprawnie i trwale usuwa przedmiot z bazy"""
    item = Item(
        name="Zły czujnik (do odrzucenia)", price=15.0, currency="PLN", status="pending",
        product_subcategory_id=mock_db["subcat"].product_subcategory_id,
        student_id=mock_db["normal_student"].student_id,
        shop_id=mock_db["shop"].shop_id,
        created_at=datetime.now()
    )
    session.add(item)
    session.commit()

    deleted_item_id = item.item_id

    response = client.delete(f"/api/items/{deleted_item_id}/reject")
    assert response.status_code == 200

    db_item = session.exec(select(Item).where(Item.item_id == deleted_item_id)).first()
    assert db_item is None

def test_fetch_pending_items_endpoint(client, session, mock_db):
    """Test: Pobieranie przedmiotów do akceptacji powinno zwracać tylko te o statusie 'pending'"""
    item_pending = Item(
        name="Czeka na decyzje", price=10.0, currency="PLN", status="pending",
        product_subcategory_id=mock_db["subcat"].product_subcategory_id,
        student_id=mock_db["normal_student"].student_id,
        shop_id=mock_db["shop"].shop_id,
        created_at=datetime.now()
    )
    item_approved = Item(
        name="Już zaakceptowany", price=20.0, currency="PLN", status="approved",
        product_subcategory_id=mock_db["subcat"].product_subcategory_id,
        student_id=mock_db["normal_student"].student_id,
        shop_id=mock_db["shop"].shop_id,
        created_at=datetime.now()
    )
    session.add_all([item_pending, item_approved])
    session.commit()

    my_association_id = mock_db["treasurer"].association_id
    response = client.get(f"/api/items/pending?association_id={my_association_id}")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Czeka na decyzje"