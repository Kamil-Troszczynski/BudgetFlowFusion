from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Enum as SQLEnum
from datetime import datetime, date
from typing import Optional
from enum import Enum


class InvoiceStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    paid = "paid"


class Currency(str, Enum):
    PLN = "PLN"
    EUR = "EUR"
    USD = "USD"

class ItemStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class AssociationBudget(SQLModel, table=True):
    __tablename__ = "association_budget"

    association_budget_id: Optional[int] = Field(default=None, primary_key=True)
    association_budget_name: str
    total_budget: float
    spent_money: float
    public_purchase_plan_list_id: Optional[int] = Field(default=None, foreign_key="public_purchase_plan_list.public_purchase_plan_list_id")

    project_budgets: list["ProjectBudget"] = Relationship(back_populates="association_budget")
    fundings: list["Funding"] = Relationship(back_populates="association_budget")


class ProjectBudget(SQLModel, table=True):
    __tablename__ = "project_budget"

    project_budget_id: Optional[int] = Field(default=None, primary_key=True)
    project_budget_name: str
    total_budget: float
    spent_money: float = 0.0

    association_budget_id: int = Field(foreign_key="association_budget.association_budget_id")
    project_id: int = Field(foreign_key="project.project_id", unique=True)

    association_budget: Optional[AssociationBudget] = Relationship(back_populates="project_budgets")
    project: Optional["Project"] = Relationship(back_populates="project_budget")
    fundings: list["Funding"] = Relationship(back_populates="project_budget")
    purchase_requests: list["PurchaseRequest"] = Relationship(back_populates="project_budget")


class PurchaseRequest(SQLModel, table=True):
    __tablename__ = "purchase_request"

    purchase_request_id: Optional[int] = Field(default=None, primary_key=True)
    purchase_request_name: str
    budget_allocated_for_the_order: float
    if_service: bool
    used_cpv_id: Optional[str] = Field(default=None)
    created_at: datetime
    can_add: bool
    document_request_name: Optional[str] = Field(default=None)
    contract_value_date: Optional[date] = Field(default=None)
    euro_exchange_rate: Optional[float] = Field(default=None)
    main_cpv_code: Optional[str] = Field(default=None)
    final_net_total: Optional[float] = Field(default=None)
    final_gross_total: Optional[float] = Field(default=None)
    finalization_status: str = Field(default="draft")
    finalized_at: Optional[datetime] = Field(default=None)

    project_budget_id: int = Field(foreign_key="project_budget.project_budget_id")
    funding_id: int = Field(foreign_key="funding.funding_id")
    public_purchase_plan_id: Optional[int] = Field(
        default=None, foreign_key="public_purchase_plan.public_purchase_plan_id"
    )
    plan_exception_justification: Optional[str] = Field(default=None)
    plan_compliance_status: str = Field(default="compliant")
    gslbccf_id: Optional[int] = Field(default=None, foreign_key="grouped_shops_list_by_cpv_category_and_funding.gslbccf_id")
    project_finance_manager_id: Optional[int] = Field(default=None, foreign_key="project_finance_manager.project_finance_manager_id") 

    project_budget: Optional[ProjectBudget] = Relationship(back_populates="purchase_requests")
    funding: Optional["Funding"] = Relationship(back_populates="purchase_requests")
    public_purchase_plan: Optional["PublicPurchasePlan"] = Relationship(back_populates="purchase_requests")
    grouped_shops_list: Optional["GroupedShopsListByCpvCategoryAndFunding"] = Relationship(back_populates="purchase_requests")
    settlements: list["Settlement"] = Relationship(back_populates="purchase_request")
    project_finance_manager: Optional["ProjectFinanceManager"] = Relationship(back_populates="purchase_requests")


class PurchaseRequestFinalizationSnapshot(SQLModel, table=True):
    __tablename__ = "purchase_request_finalization_snapshot"

    snapshot_id: Optional[int] = Field(default=None, primary_key=True)
    purchase_request_id: int = Field(foreign_key="purchase_request.purchase_request_id")
    shop_purchase_list_id: Optional[int] = Field(default=None, foreign_key="shop_purchase_list.shop_purchase_list_id")
    public_purchase_plan_id: Optional[int] = Field(default=None, foreign_key="public_purchase_plan.public_purchase_plan_id")
    funding_id: Optional[int] = Field(default=None, foreign_key="funding.funding_id")
    shop_name: Optional[str] = Field(default=None)
    funding_name: Optional[str] = Field(default=None)
    plan_name: Optional[str] = Field(default=None)
    plan_number: Optional[str] = Field(default=None)
    fund_responsible_person: Optional[str] = Field(default=None)
    plan_position_number: Optional[str] = Field(default=None)
    cpv_code: Optional[str] = Field(default=None)
    planned_net_amount: float = 0.0
    allocated_net_amount: float = 0.0
    allocated_eur_amount: float = 0.0
    allocated_gross_amount: float = 0.0
    is_main_cpv: bool = False
    created_at: datetime


class PurchaseRequestSettlementLine(SQLModel, table=True):
    __tablename__ = "purchase_request_settlement_line"

    settlement_line_id: Optional[int] = Field(default=None, primary_key=True)
    purchase_request_id: int = Field(foreign_key="purchase_request.purchase_request_id")
    shop_purchase_list_id: Optional[int] = Field(default=None, foreign_key="shop_purchase_list.shop_purchase_list_id")
    invoice_id: Optional[int] = Field(default=None, foreign_key="invoice.invoice_id")
    shop_name: str
    purchase_description: Optional[str] = Field(default=None)
    planned_gross_amount: float = 0.0
    actual_gross_amount: Optional[float] = Field(default=None)
    is_extra: bool = Field(default=False)
    created_at: datetime
    updated_at: Optional[datetime] = Field(default=None)


class PurchaseRequestFundingAllocation(SQLModel, table=True):
    __tablename__ = "purchase_request_funding_allocation"

    purchase_request_id: int = Field(foreign_key="purchase_request.purchase_request_id", primary_key=True)
    funding_id: int = Field(foreign_key="funding.funding_id", primary_key=True)
    allocated_amount: float


class PurchaseRequestPlanPosition(SQLModel, table=True):
    __tablename__ = "purchase_request_plan_position"

    purchase_request_id: int = Field(foreign_key="purchase_request.purchase_request_id", primary_key=True)
    shop_purchase_list_id: int = Field(foreign_key="shop_purchase_list.shop_purchase_list_id", primary_key=True)
    public_purchase_plan_id: int = Field(foreign_key="public_purchase_plan.public_purchase_plan_id", primary_key=True)
    allocated_amount: float



class PublicPurchasePlanList(SQLModel, table=True):
    __tablename__ = "public_purchase_plan_list"

    public_purchase_plan_list_id: Optional[int] = Field(default=None, primary_key=True)
    public_plan_list_name: str
    plan_year: int
    plan_number: Optional[str] = Field(default=None)
    fund_responsible_person: Optional[str] = Field(default=None)
    euro_exchange_rate: Optional[float] = Field(default=None)
    funding_id: int = Field(foreign_key="funding.funding_id", unique=True)

    funding: Optional["Funding"] = Relationship(back_populates="public_purchase_plan_list")
    public_purchase_plans: list["PublicPurchasePlan"] = Relationship(back_populates="public_purchase_plan_list")


class Funding(SQLModel, table=True):
    __tablename__ = "funding"

    funding_id: Optional[int] = Field(default=None, primary_key=True)
    funding_name: str
    organizer: Optional[str] = Field(default=None)
    signing_person: Optional[str] = Field(default=None)
    spending_deadline: Optional[date] = Field(default=None)
    funding_price: float
    spent_money: float

    project_id: Optional[int] = Field(default=None, foreign_key="project.project_id")
    project_budget_id: int = Field(foreign_key="project_budget.project_budget_id")
    association_budget_id: int = Field(foreign_key="association_budget.association_budget_id")

    association_budget: Optional[AssociationBudget] = Relationship(back_populates="fundings")
    project: Optional["Project"] = Relationship(back_populates="fundings")
    project_budget: Optional[ProjectBudget] = Relationship(back_populates="fundings")
    purchase_requests: list[PurchaseRequest] = Relationship(back_populates="funding")
    shop_purchase_lists: list["ShopPurchaseList"] = Relationship(back_populates="funding")
    public_purchase_plan_list: Optional[PublicPurchasePlanList] = Relationship(back_populates="funding")
    tasks: list["FundingTask"] = Relationship(back_populates="funding")


class FundingTask(SQLModel, table=True):
    __tablename__ = "funding_task"

    funding_task_id: Optional[int] = Field(default=None, primary_key=True)
    funding_id: int = Field(foreign_key="funding.funding_id")
    task_name: str
    task_budget: float

    funding: Optional[Funding] = Relationship(back_populates="tasks")


class Settlement(SQLModel, table=True):
    __tablename__ = "settlement"

    settlement_id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime

    paid_by_project_finance_manager_id: Optional[int] = Field(default=None, foreign_key="project_finance_manager.project_finance_manager_id")
    purchase_request_id: Optional[int] = Field(default=None, foreign_key="purchase_request.purchase_request_id")

    purchase_request: Optional[PurchaseRequest] = Relationship(back_populates="settlements")
    paid_by_project_finance_manager: Optional["ProjectFinanceManager"] = Relationship(back_populates="paid_settlements")
    invoices: list["Invoice"] = Relationship(back_populates="settlement")
    shop_purchase_lists: list["ShopPurchaseList"] = Relationship(back_populates="settlement")


class GroupedShopsListByCpvCategoryAndFunding(SQLModel, table=True):
    __tablename__ = "grouped_shops_list_by_cpv_category_and_funding"

    gslbccf_id: Optional[int] = Field(default=None, primary_key=True)
    allocated_money: float

    purchase_requests: Optional[PurchaseRequest] = Relationship(back_populates="grouped_shops_list")
    public_purchase_plans: list["PublicPurchasePlan"] = Relationship(back_populates="grouped_shops_list")
    shop_purchase_lists: list["ShopPurchaseList"] = Relationship(back_populates="grouped_shops_list")


class ProjectFinanceManager(SQLModel, table=True):
    __tablename__ = "project_finance_manager"

    project_finance_manager_id: Optional[int] = Field(default=None, primary_key=True)
    login: str
    password_hash: str = Field(max_length=256)
    access: bool

    paid_settlements: list[Settlement] = Relationship(back_populates="paid_by_project_finance_manager")
    student: Optional["Student"] = Relationship(back_populates="project_finance_manager")
    purchase_requests: list["PurchaseRequest"] = Relationship(back_populates="project_finance_manager") 


class PublicPurchasePlan(SQLModel, table=True):
    __tablename__ = "public_purchase_plan"

    public_purchase_plan_id: Optional[int] = Field(default=None, primary_key=True)
    public_purchase_plan_name: str
    cpv_code: str
    plan_position_number: Optional[str] = Field(default=None)
    cost: float

    funding_id: Optional[int] = Field(default=None, foreign_key="funding.funding_id")
    gslbccf_id: Optional[int] = Field(default=None, foreign_key="grouped_shops_list_by_cpv_category_and_funding.gslbccf_id")
    public_purchase_plan_list_id: int = Field(foreign_key="public_purchase_plan_list.public_purchase_plan_list_id")

    public_purchase_plan_list: Optional[PublicPurchasePlanList] = Relationship(back_populates="public_purchase_plans")
    grouped_shops_list: Optional[GroupedShopsListByCpvCategoryAndFunding] = Relationship(back_populates="public_purchase_plans")
    purchase_requests: list[PurchaseRequest] = Relationship(back_populates="public_purchase_plan")


class Project(SQLModel, table=True):
    __tablename__ = "project"

    project_id: Optional[int] = Field(default=None, primary_key=True)
    project_name: str
    description: str
    allocated_budget: float
    rest_of_budget: float

    association_id: Optional[int] = Field(default=None, foreign_key="association.association_id")
    association: Optional["Association"] = Relationship(back_populates="projects")

    fundings: list[Funding] = Relationship(back_populates="project")
    project_budget: Optional[ProjectBudget] = Relationship(back_populates="project")


class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"

    invoice_id: Optional[int] = Field(default=None, primary_key=True)
    number: str
    issue_date: date
    seller_name: str
    seller_nip: str
    net_total: float
    vat_total: float
    status: InvoiceStatus = Field(sa_column=Column(SQLEnum(InvoiceStatus), nullable=False))
    created_at: datetime
    settlement_id: Optional[int] = Field(default=None, foreign_key="settlement.settlement_id")

    settlement: Optional[Settlement] = Relationship(back_populates="invoices")


class ProductCategory(SQLModel, table=True):
    __tablename__ = "product_category"

    product_category_id: Optional[int] = Field(default=None, primary_key=True)
    product_category_name: str
    description: str
    cpv: str | None = Field(default=None)

    shop_purchase_list_id: Optional[int] = Field(default=None, foreign_key="shop_purchase_list.shop_purchase_list_id")
    public_purchase_plan_id: Optional[int] = Field(default=None, foreign_key="public_purchase_plan.public_purchase_plan_id")

    product_subcategories: list["ProductSubcategory"] = Relationship(back_populates="product_category")
    shop_purchase_list: Optional["ShopPurchaseList"] = Relationship(back_populates="product_categories")


class ProductSubcategory(SQLModel, table=True):
    __tablename__ = "product_subcategory"

    product_subcategory_id: Optional[int] = Field(default=None, primary_key=True)
    product_subcategory_name: str
    description: str
    product_category_id: Optional[int] = Field(default=None, foreign_key="product_category.product_category_id")

    product_category: Optional[ProductCategory] = Relationship(back_populates="product_subcategories")
    items: list["Item"] = Relationship(back_populates="product_subcategory")


class Shop(SQLModel, table=True):
    __tablename__ = "shop"

    shop_id: Optional[int] = Field(default=None, primary_key=True)
    shop_name: str
    link: Optional[str] = Field(default=None)
    opinion: Optional[str] = Field(default=None)
    status: str = Field(default="approved")
    created_by_student_id: Optional[int] = Field(default=None)
    address: str
    delivery_time: datetime
    is_recommended: bool
    free_delivery_threshold: float

    shop_purchase_lists: list["ShopPurchaseList"] = Relationship(back_populates="shop")
    items: list["Item"] = Relationship(back_populates="shop")


class Item(SQLModel, table=True):
    __tablename__ = "item"

    item_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    currency: Currency = Field(sa_column=Column(SQLEnum(Currency), nullable=False))
    link: str | None = Field(default=None)
    created_at: datetime
    tax_rate: float = Field(default=23.0)

    status: str = Field(default="approved")

    product_subcategory_id: int = Field(foreign_key="product_subcategory.product_subcategory_id")
    student_id: int = Field(foreign_key="student.student_id")
    shop_id: int = Field(foreign_key="shop.shop_id")
    product_subcategory: Optional[ProductSubcategory] = Relationship(back_populates="items")
    student: Optional["Student"] = Relationship(back_populates="items")
    shop: Optional[Shop] = Relationship(back_populates="items")
    shop_purchase_list_items: list["ShopPurchaseListItem"] = Relationship(back_populates="item")


class ShopPurchaseListItem(SQLModel, table=True):
    __tablename__ = "shop_purchase_list_item"

    shop_purchase_list_id: int = Field(foreign_key="shop_purchase_list.shop_purchase_list_id", primary_key=True)
    item_id: int = Field(foreign_key="item.item_id", primary_key=True)

    shop_purchase_list: Optional["ShopPurchaseList"] = Relationship(back_populates="shop_purchase_list_items")
    item: Optional[Item] = Relationship(back_populates="shop_purchase_list_items")
    amount: int


class ShopPurchaseListItemContribution(SQLModel, table=True):
    __tablename__ = "shop_purchase_list_item_contribution"

    shop_purchase_list_id: int = Field(foreign_key="shop_purchase_list.shop_purchase_list_id", primary_key=True)
    item_id: int = Field(foreign_key="item.item_id", primary_key=True)
    student_id: int = Field(foreign_key="student.student_id", primary_key=True)
    amount: int
    created_at: datetime


class Student(SQLModel, table=True):
    __tablename__ = "student"

    student_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    surname: str
    login: str
    password_hash: str = Field(max_length=256)
    position: str
    is_in_sap: bool
    project_finance_manager_id: Optional[int] = Field(default=None, foreign_key="project_finance_manager.project_finance_manager_id")

    association_id: Optional[int] = Field(default=None, foreign_key="association.association_id")
    association: Optional["Association"] = Relationship(back_populates="students")

    project_finance_manager: Optional[ProjectFinanceManager] = Relationship(back_populates="student")
    items: list["Item"] = Relationship(back_populates="student")
    shop_purchase_lists: list["ShopPurchaseList"] = Relationship(back_populates="student")


class ShopPurchaseList(SQLModel, table=True):
    __tablename__ = "shop_purchase_list"

    shop_purchase_list_id: Optional[int] = Field(default=None, primary_key=True)
    priority: int
    name: str | None = Field(default=None)
    cost: float
    created_at: datetime
    market_research_comment: str | None = Field(default=None)
    market_research_file_name: str | None = Field(default=None)

    gslbccf_id: Optional[int] = Field(default=None, foreign_key="grouped_shops_list_by_cpv_category_and_funding.gslbccf_id")
    settlement_id: Optional[int] = Field(default=None, foreign_key="settlement.settlement_id")
    funding_id: int = Field(foreign_key="funding.funding_id")
    shop_id: int = Field(foreign_key="shop.shop_id")
    student_id: int = Field(foreign_key="student.student_id")

    funding: Optional[Funding] = Relationship(back_populates="shop_purchase_lists")
    shop: Optional[Shop] = Relationship(back_populates="shop_purchase_lists")
    settlement: Optional[Settlement] = Relationship(back_populates="shop_purchase_lists")
    grouped_shops_list: Optional[GroupedShopsListByCpvCategoryAndFunding] = Relationship(back_populates="shop_purchase_lists")
    student: Optional[Student] = Relationship(back_populates="shop_purchase_lists")
    product_categories: list[ProductCategory] = Relationship(back_populates="shop_purchase_list")
    shop_purchase_list_items: list[ShopPurchaseListItem] = Relationship(back_populates="shop_purchase_list")

class Association(SQLModel, table=True):
    __tablename__ = "association"

    association_id: Optional[int] = Field(default=None, primary_key=True)
    association_name: str

    students: list["Student"] = Relationship(back_populates="association")
    projects: list["Project"] = Relationship(back_populates="association")
