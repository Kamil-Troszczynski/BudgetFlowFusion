from sqlmodel import SQLModel, Session, create_engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import inspect, text
from src.relations import *
import os


path = os.getenv('DATABASE_URL')
engine = create_engine(path)


MOCKUP_DATA_FILEPATH = "scripts/mockup_data.sql"


def prepare_database(mockup_data_filepath: str):
    SQLModel.metadata.create_all(engine)
    migrate_project_budgets()
    with Session(engine) as session:
        try:
            with open(mockup_data_filepath, 'r') as file:
                sql_instructions = text(file.read())
            session.exec(sql_instructions)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"SQL instructions failed - exception {e}")


def migrate_project_budgets():
    if engine.dialect.name != "postgresql":
        return

    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "purchase_request" not in table_names:
        return

    purchase_request_columns = {
        column["name"] for column in inspector.get_columns("purchase_request")
    }
    funding_columns = {
        column["name"] for column in inspector.get_columns("funding")
    }
    plan_list_columns = {
        column["name"]
        for column in inspector.get_columns("public_purchase_plan_list")
    }
    plan_columns = {
        column["name"] for column in inspector.get_columns("public_purchase_plan")
    }
    item_columns = (
        {column["name"] for column in inspector.get_columns("item")}
        if "item" in table_names
        else set()
    )
    shop_columns = (
        {column["name"] for column in inspector.get_columns("shop")}
        if "shop" in table_names
        else set()
    )
    plan_position_columns = (
        {
            column["name"]
            for column in inspector.get_columns("purchase_request_plan_position")
        }
        if "purchase_request_plan_position" in table_names
        else set()
    )
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS purchase_request_funding_allocation (
                purchase_request_id INTEGER NOT NULL REFERENCES purchase_request(purchase_request_id) ON DELETE CASCADE,
                funding_id INTEGER NOT NULL REFERENCES funding(funding_id),
                allocated_amount DOUBLE PRECISION NOT NULL,
                PRIMARY KEY (purchase_request_id, funding_id)
            )
        """))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS purchase_request_plan_position (
                purchase_request_id INTEGER NOT NULL REFERENCES purchase_request(purchase_request_id) ON DELETE CASCADE,
                shop_purchase_list_id INTEGER NOT NULL REFERENCES shop_purchase_list(shop_purchase_list_id),
                public_purchase_plan_id INTEGER NOT NULL REFERENCES public_purchase_plan(public_purchase_plan_id),
                allocated_amount DOUBLE PRECISION NOT NULL,
                PRIMARY KEY (purchase_request_id, shop_purchase_list_id, public_purchase_plan_id)
            )
        """))
        if (
            "purchase_request_plan_position" in table_names
            and "shop_purchase_list_id" not in plan_position_columns
        ):
            connection.execute(text("""
                ALTER TABLE purchase_request_plan_position
                ADD COLUMN shop_purchase_list_id INTEGER
                REFERENCES shop_purchase_list(shop_purchase_list_id)
            """))
            connection.execute(text("""
                UPDATE purchase_request_plan_position AS position
                SET shop_purchase_list_id = first_list.shop_purchase_list_id
                FROM purchase_request
                JOIN LATERAL (
                    SELECT shop_purchase_list.shop_purchase_list_id
                    FROM shop_purchase_list
                    WHERE shop_purchase_list.gslbccf_id = purchase_request.gslbccf_id
                    ORDER BY shop_purchase_list.shop_purchase_list_id
                    LIMIT 1
                ) AS first_list ON TRUE
                WHERE purchase_request.purchase_request_id = position.purchase_request_id
                  AND position.shop_purchase_list_id IS NULL
            """))
            connection.execute(text("""
                DELETE FROM purchase_request_plan_position
                WHERE shop_purchase_list_id IS NULL
            """))
            connection.execute(text("""
                ALTER TABLE purchase_request_plan_position
                ALTER COLUMN shop_purchase_list_id SET NOT NULL
            """))
            connection.execute(text("""
                ALTER TABLE purchase_request_plan_position
                DROP CONSTRAINT IF EXISTS purchase_request_plan_position_pkey
            """))
            connection.execute(text("""
                ALTER TABLE purchase_request_plan_position
                ADD PRIMARY KEY (
                    purchase_request_id,
                    shop_purchase_list_id,
                    public_purchase_plan_id
                )
            """))
        if "project_budget_id" not in purchase_request_columns:
            connection.execute(text(
                "ALTER TABLE purchase_request ADD COLUMN project_budget_id INTEGER"
            ))
        if "funding_id" not in purchase_request_columns:
            connection.execute(text(
                "ALTER TABLE purchase_request ADD COLUMN funding_id INTEGER"
            ))
        if "public_purchase_plan_id" not in purchase_request_columns:
            connection.execute(text(
                "ALTER TABLE purchase_request ADD COLUMN public_purchase_plan_id INTEGER"
            ))
        if "plan_exception_justification" not in purchase_request_columns:
            connection.execute(text(
                "ALTER TABLE purchase_request ADD COLUMN plan_exception_justification VARCHAR"
            ))
        if "plan_compliance_status" not in purchase_request_columns:
            connection.execute(text(
                "ALTER TABLE purchase_request "
                "ADD COLUMN plan_compliance_status VARCHAR DEFAULT 'compliant'"
            ))
        if "funding_id" not in plan_list_columns:
            connection.execute(text(
                "ALTER TABLE public_purchase_plan_list ADD COLUMN funding_id INTEGER"
            ))
        if "plan_year" not in plan_list_columns:
            connection.execute(text(
                "ALTER TABLE public_purchase_plan_list ADD COLUMN plan_year INTEGER DEFAULT 2026"
            ))
        if "cpv_code" not in plan_columns:
            connection.execute(text(
                "ALTER TABLE public_purchase_plan ADD COLUMN cpv_code INTEGER"
            ))
        if "tax_rate" not in item_columns:
            connection.execute(text(
                "ALTER TABLE item ADD COLUMN tax_rate DOUBLE PRECISION DEFAULT 23"
            ))
        if "link" not in shop_columns:
            connection.execute(text("ALTER TABLE shop ADD COLUMN link VARCHAR"))
        if "opinion" not in shop_columns:
            connection.execute(text("ALTER TABLE shop ADD COLUMN opinion VARCHAR"))
        if "status" not in shop_columns:
            connection.execute(text(
                "ALTER TABLE shop ADD COLUMN status VARCHAR DEFAULT 'approved'"
            ))
        if "created_by_student_id" not in shop_columns:
            connection.execute(text(
                "ALTER TABLE shop ADD COLUMN created_by_student_id INTEGER"
            ))
        connection.execute(text(
            "UPDATE shop SET status = 'approved' WHERE status IS NULL"
        ))

        connection.execute(text("""
            UPDATE public_purchase_plan
            SET cpv_code = COALESCE(
                cpv_code,
                NULLIF(
                    split_part(
                        (
                            SELECT product_category.cpv
                            FROM product_category
                            WHERE product_category.public_purchase_plan_id =
                                public_purchase_plan.public_purchase_plan_id
                            LIMIT 1
                        ),
                        '-',
                        1
                    ),
                    ''
                )::INTEGER,
                1
            )
            WHERE cpv_code IS NULL
        """))
        connection.execute(text("""
            UPDATE public_purchase_plan_list AS plan_list
            SET funding_id = plan_funding.funding_id
            FROM (
                SELECT public_purchase_plan_list_id, MIN(funding_id) AS funding_id
                FROM public_purchase_plan
                WHERE funding_id IS NOT NULL
                GROUP BY public_purchase_plan_list_id
            ) AS plan_funding
            WHERE plan_funding.public_purchase_plan_list_id =
                plan_list.public_purchase_plan_list_id
              AND plan_list.funding_id IS NULL
        """))
        connection.execute(text("""
            INSERT INTO public_purchase_plan_list (
                public_plan_list_name,
                plan_year,
                funding_id
            )
            SELECT
                'Plan ZP - ' || funding.funding_name,
                EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER,
                funding.funding_id
            FROM funding
            WHERE NOT EXISTS (
                SELECT 1
                FROM public_purchase_plan_list
                WHERE public_purchase_plan_list.funding_id = funding.funding_id
            )
        """))
        connection.execute(text("""
            UPDATE public_purchase_plan AS plan
            SET public_purchase_plan_list_id =
                plan_list.public_purchase_plan_list_id
            FROM public_purchase_plan_list AS plan_list
            WHERE plan.funding_id = plan_list.funding_id
              AND plan.public_purchase_plan_list_id !=
                  plan_list.public_purchase_plan_list_id
        """))

        connection.execute(text("""
            INSERT INTO project_budget (
                project_budget_name,
                total_budget,
                spent_money,
                association_budget_id,
                project_id
            )
            SELECT
                'Budżet sekcji: ' || project.project_name,
                SUM(funding.funding_price),
                SUM(funding.spent_money),
                MIN(funding.association_budget_id),
                project.project_id
            FROM project
            JOIN funding ON funding.project_id = project.project_id
            LEFT JOIN project_budget ON project_budget.project_id = project.project_id
            WHERE project_budget.project_budget_id IS NULL
            GROUP BY project.project_id, project.project_name
        """))

        if "project_budget_id" not in funding_columns:
            connection.execute(text(
                "ALTER TABLE funding ADD COLUMN project_budget_id INTEGER"
            ))

        connection.execute(text("""
            UPDATE funding AS funding
            SET project_budget_id = project_budget.project_budget_id
            FROM project_budget
            WHERE project_budget.project_id = funding.project_id
              AND funding.project_budget_id IS NULL
        """))

        connection.execute(text("""
            UPDATE funding AS funding
            SET association_budget_id = project_budget.association_budget_id
            FROM project_budget
            WHERE project_budget.project_budget_id = funding.project_budget_id
        """))

        connection.execute(text(
            "ALTER TABLE funding ALTER COLUMN project_budget_id SET NOT NULL"
        ))

        connection.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'funding_project_budget_id_fkey'
                ) THEN
                    ALTER TABLE funding
                    ADD CONSTRAINT funding_project_budget_id_fkey
                    FOREIGN KEY (project_budget_id)
                    REFERENCES project_budget(project_budget_id);
                END IF;
            END $$
        """))
        connection.execute(text("""
            INSERT INTO purchase_request_funding_allocation (
                purchase_request_id,
                funding_id,
                allocated_amount
            )
            SELECT
                purchase_request_id,
                funding_id,
                budget_allocated_for_the_order
            FROM purchase_request
            WHERE funding_id IS NOT NULL
              AND budget_allocated_for_the_order > 0
              AND NOT EXISTS (
                  SELECT 1
                  FROM purchase_request_funding_allocation allocation
                  WHERE allocation.purchase_request_id = purchase_request.purchase_request_id
              )
        """))
        connection.execute(text("""
            INSERT INTO purchase_request_plan_position (
                purchase_request_id,
                shop_purchase_list_id,
                public_purchase_plan_id,
                allocated_amount
            )
            SELECT
                purchase_request.purchase_request_id,
                shop_purchase_list.shop_purchase_list_id,
                purchase_request.public_purchase_plan_id,
                purchase_request.budget_allocated_for_the_order / 1.23
            FROM purchase_request
            JOIN shop_purchase_list
              ON shop_purchase_list.gslbccf_id = purchase_request.gslbccf_id
            WHERE purchase_request.public_purchase_plan_id IS NOT NULL
              AND purchase_request.budget_allocated_for_the_order > 0
              AND NOT EXISTS (
                  SELECT 1
                  FROM purchase_request_plan_position position
                  WHERE position.purchase_request_id = purchase_request.purchase_request_id
                    AND position.shop_purchase_list_id = shop_purchase_list.shop_purchase_list_id
                    AND position.public_purchase_plan_id = purchase_request.public_purchase_plan_id
              )
        """))

        connection.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'public_purchase_plan_list_funding_id_fkey'
                ) THEN
                    ALTER TABLE public_purchase_plan_list
                    ADD CONSTRAINT public_purchase_plan_list_funding_id_fkey
                    FOREIGN KEY (funding_id)
                    REFERENCES funding(funding_id);
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'purchase_request_public_purchase_plan_id_fkey'
                ) THEN
                    ALTER TABLE purchase_request
                    ADD CONSTRAINT purchase_request_public_purchase_plan_id_fkey
                    FOREIGN KEY (public_purchase_plan_id)
                    REFERENCES public_purchase_plan(public_purchase_plan_id);
                END IF;
            END $$
        """))

        connection.execute(text("""
            UPDATE project_budget AS project_budget
            SET total_budget = funding_totals.total_budget,
                spent_money = funding_totals.spent_money
            FROM (
                SELECT
                    project_budget_id,
                    SUM(funding_price) AS total_budget,
                    SUM(spent_money) AS spent_money
                FROM funding
                WHERE project_budget_id IS NOT NULL
                GROUP BY project_budget_id
            ) AS funding_totals
            WHERE funding_totals.project_budget_id = project_budget.project_budget_id
        """))

        connection.execute(text("""
            UPDATE association_budget AS association_budget
            SET total_budget = project_totals.total_budget,
                spent_money = project_totals.spent_money
            FROM (
                SELECT
                    association_budget_id,
                    SUM(total_budget) AS total_budget,
                    SUM(spent_money) AS spent_money
                FROM project_budget
                GROUP BY association_budget_id
            ) AS project_totals
            WHERE project_totals.association_budget_id = association_budget.association_budget_id
        """))

        if "association_budget_id" in purchase_request_columns:
            connection.execute(text("""
                UPDATE purchase_request AS purchase_request
                SET project_budget_id = project_budget.project_budget_id
                FROM settlement
                JOIN shop_purchase_list
                    ON shop_purchase_list.settlement_id = settlement.settlement_id
                JOIN funding ON funding.funding_id = shop_purchase_list.funding_id
                JOIN project_budget ON project_budget.project_id = funding.project_id
                WHERE settlement.purchase_request_id = purchase_request.purchase_request_id
                  AND purchase_request.project_budget_id IS NULL
            """))
            connection.execute(text("""
                UPDATE purchase_request AS purchase_request
                SET project_budget_id = fallback.project_budget_id
                FROM (
                    SELECT association_budget_id, MIN(project_budget_id) AS project_budget_id
                    FROM project_budget
                    GROUP BY association_budget_id
                ) AS fallback
                WHERE fallback.association_budget_id = purchase_request.association_budget_id
                  AND purchase_request.project_budget_id IS NULL
            """))
            connection.execute(text(
                "ALTER TABLE purchase_request ALTER COLUMN association_budget_id DROP NOT NULL"
            ))

        connection.execute(text("""
            UPDATE purchase_request AS purchase_request
            SET funding_id = shop_purchase_list.funding_id
            FROM settlement
            JOIN shop_purchase_list
                ON shop_purchase_list.settlement_id = settlement.settlement_id
            WHERE settlement.purchase_request_id = purchase_request.purchase_request_id
              AND purchase_request.funding_id IS NULL
        """))
        connection.execute(text("""
            UPDATE purchase_request AS purchase_request
            SET funding_id = fallback.funding_id
            FROM (
                SELECT project_budget_id, MIN(funding_id) AS funding_id
                FROM funding
                GROUP BY project_budget_id
            ) AS fallback
            WHERE fallback.project_budget_id = purchase_request.project_budget_id
              AND purchase_request.funding_id IS NULL
        """))
        connection.execute(text(
            "ALTER TABLE purchase_request ALTER COLUMN funding_id SET NOT NULL"
        ))

        connection.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'purchase_request_funding_id_fkey'
                ) THEN
                    ALTER TABLE purchase_request
                    ADD CONSTRAINT purchase_request_funding_id_fkey
                    FOREIGN KEY (funding_id)
                    REFERENCES funding(funding_id);
                END IF;
            END $$
        """))

        connection.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'purchase_request_project_budget_id_fkey'
                ) THEN
                    ALTER TABLE purchase_request
                    ADD CONSTRAINT purchase_request_project_budget_id_fkey
                    FOREIGN KEY (project_budget_id)
                    REFERENCES project_budget(project_budget_id);
                END IF;
            END $$
        """))


@asynccontextmanager
async def lifespan(app):
    prepare_database(MOCKUP_DATA_FILEPATH)
    yield


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI(lifespan = lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import src.routes
