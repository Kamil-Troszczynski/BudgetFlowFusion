import os
from sqlmodel import SQLModel, Session, create_engine, select
from dotenv import load_dotenv
from datetime import datetime, timedelta, date

from src.relations import (
    Project, Funding, AssociationBudget, ProductCategory,
    ProductSubcategory, Shop, Currency, Item, ShopPurchaseList,
    ShopPurchaseListItem, Student, ProjectFinanceManager, InvoiceStatus,
    GroupedShopsListByCpvCategoryAndFunding, PublicPurchasePlanList,
    PublicPurchasePlan, PurchaseRequest, Settlement, Invoice
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://budgetflowfusion:budgetflowfusion@db:5432/budgetflowfusion")
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        if not session.exec(select(AssociationBudget)).first():
            treasurer_role = ProjectFinanceManager(login="skarbnik_glowny", password_hash="hashed_123", access=True)
            session.add(treasurer_role)
            session.commit()
            session.refresh(treasurer_role)

            student_treasurer = Student(name="Michał", surname="Kowalski", login="mkowalski", password_hash="hashed_123", position="Skarbnik", is_in_sap=True, project_finance_manager_id=treasurer_role.project_finance_manager_id)
            student_engineer = Student(name="Anna", surname="Nowak", login="anowak", password_hash="hashed_456", position="Główny Mechanik", is_in_sap=False)

            session.add_all([student_treasurer, student_engineer])
            session.commit()
            session.refresh(student_engineer)

            main_budget = AssociationBudget(association_budget_name="Budżet Główny Koła 2026", total_budget=500000.0, spent_money=0.0)
            session.add(main_budget)
            session.commit()
            session.refresh(main_budget)

            project_hal = Project(project_name="Łazik Marsjański HAL_062", description="Projekt zaawansowanego łazika badawczego.", allocated_budget=25000.0, rest_of_budget=25000.0)
            project_vtol = Project(project_name="Platforma VTOL Tail-sitter", description="Bezzałogowiec o pionowym starcie.", allocated_budget=8000.0, rest_of_budget=8000.0)
            session.add_all([project_hal, project_vtol])
            session.commit()
            session.refresh(project_hal)
            session.refresh(project_vtol)

            funding_hal = Funding(funding_name="Grant Rektora - HAL_062", funding_price=20000.0, spent_money=0.0, project_id=project_hal.project_id, association_budget_id=main_budget.association_budget_id)
            session.add(funding_hal)
            session.commit()
            session.refresh(funding_hal)

            cat_mechanics = ProductCategory(product_category_name="Mechanika i Napędy", description="Silniki", cpv_id=42000000)
            cat_electronics = ProductCategory(product_category_name="Elektronika i Zasilanie", description="Czujniki", cpv_id=31700000)
            cat_materials = ProductCategory(product_category_name="Materiały Konstrukcyjne", description="Filamenty", cpv_id=44000000)
            session.add_all([cat_mechanics, cat_electronics, cat_materials])
            session.commit()
            session.refresh(cat_mechanics)
            session.refresh(cat_electronics)
            session.refresh(cat_materials)

            sub_motors = ProductSubcategory(product_subcategory_name="Silniki DC/BLDC", description="", product_category_id=cat_mechanics.product_category_id)
            sub_sensors = ProductSubcategory(product_subcategory_name="Systemy Wizyjne", description="", product_category_id=cat_electronics.product_category_id)
            sub_raw = ProductSubcategory(product_subcategory_name="Druk 3D i Pianki", description="", product_category_id=cat_materials.product_category_id)
            session.add_all([sub_motors, sub_sensors, sub_raw])
            session.commit()
            session.refresh(sub_motors)
            session.refresh(sub_sensors)
            session.refresh(sub_raw)

            shop_botland = Shop(shop_name="Botland", address="Online", delivery_time=datetime.now() + timedelta(days=2), is_recommended=True, free_delivery_threshold=200.0)
            session.add(shop_botland)
            session.commit()
            session.refresh(shop_botland)

            grouped_shops_hal = GroupedShopsListByCpvCategoryAndFunding(allocated_money=20000.0)
            session.add(grouped_shops_hal)
            session.commit()
            session.refresh(grouped_shops_hal)

            plan_list = PublicPurchasePlanList(public_plan_list_name="Plan Zamówień Publicznych Koła 2026")
            session.add(plan_list)
            session.commit()
            session.refresh(plan_list)

            main_budget.public_purchase_plan_list_id = plan_list.public_purchase_plan_list_id
            session.add(main_budget)
            session.commit()

            public_plan_hal = PublicPurchasePlan(
                public_purchase_plan_name="Zakup podzespołów napędowych do łazika HAL_062",
                cost=5000.0,
                funding_id=funding_hal.funding_id,
                gslbccf_id=grouped_shops_hal.gslbccf_id,
                public_purchase_plan_list_id=plan_list.public_purchase_plan_list_id
            )
            session.add(public_plan_hal)
            session.commit()

            item_motor = Item(name="Silnik DC z przekładnią 12V", price=145.50, currency=Currency.PLN, link="https://botland.com.pl", created_at=datetime.now(), product_subcategory_id=sub_motors.product_subcategory_id, student_id=student_engineer.student_id, shop_id=shop_botland.shop_id)
            item_camera = Item(name="Kamera Intel RealSense D435i", price=1850.00, currency=Currency.PLN, link="https://botland.com.pl", created_at=datetime.now(), product_subcategory_id=sub_sensors.product_subcategory_id, student_id=student_engineer.student_id, shop_id=shop_botland.shop_id)
            item_petg = Item(name="Filament PETG 1kg Czarny", price=65.00, currency=Currency.PLN, link="https://botland.com.pl", created_at=datetime.now(), product_subcategory_id=sub_raw.product_subcategory_id, student_id=student_engineer.student_id, shop_id=shop_botland.shop_id)
            session.add_all([item_motor, item_camera, item_petg])
            session.commit()
            session.refresh(item_motor)
            session.refresh(item_camera)
            session.refresh(item_petg)

            list_hal_motors = ShopPurchaseList(
                name="Napęd i wizja - zamówienie główne",
                priority=1, cost=0.0, created_at=datetime.now(),
                funding_id=funding_hal.funding_id, shop_id=shop_botland.shop_id,
                student_id=student_engineer.student_id, gslbccf_id=grouped_shops_hal.gslbccf_id
            )
            session.add(list_hal_motors)
            session.commit()
            session.refresh(list_hal_motors)

            line_item_1 = ShopPurchaseListItem(shop_purchase_list_id=list_hal_motors.shop_purchase_list_id, item_id=item_motor.item_id, ammount=4)
            line_item_2 = ShopPurchaseListItem(shop_purchase_list_id=list_hal_motors.shop_purchase_list_id, item_id=item_camera.item_id, ammount=1)
            line_item_3 = ShopPurchaseListItem(shop_purchase_list_id=list_hal_motors.shop_purchase_list_id, item_id=item_petg.item_id, ammount=2)
            session.add_all([line_item_1, line_item_2, line_item_3])

            list_hal_motors.cost = (item_motor.price * 4) + (item_camera.price * 1) + (item_petg.price * 2)
            session.commit()

            purchase_request_hal = PurchaseRequest(
                purchase_request_name="Wniosek: Napęd i wizja łazika", budget_allocated_for_the_order=list_hal_motors.cost,
                if_service=False, used_cpv_id=cat_mechanics.cpv_id, created_at=datetime.now(), can_add=False,
                association_budget_id=main_budget.association_budget_id, gslbccf_id=grouped_shops_hal.gslbccf_id
            )
            session.add(purchase_request_hal)
            session.commit()
            session.refresh(purchase_request_hal)

            settlement_hal = Settlement(
                created_at=datetime.now(), paid_by_project_finance_manager_id=treasurer_role.project_finance_manager_id, purchase_request_id=purchase_request_hal.purchase_request_id
            )
            session.add(settlement_hal)
            session.commit()
            session.refresh(settlement_hal)

            list_hal_motors.settlement_id = settlement_hal.settlement_id
            session.add(list_hal_motors)
            session.commit()

            invoice_hal = Invoice(
                number="F/2026/05/HAL-001", issue_date=date.today(), seller_name="Botland", seller_nip="1234567890",
                net_total=list_hal_motors.cost / 1.23, vat_total=list_hal_motors.cost - (list_hal_motors.cost / 1.23),
                status=InvoiceStatus.paid, created_at=datetime.now(), settlement_id=settlement_hal.settlement_id
            )
            session.add(invoice_hal)
            session.commit()
