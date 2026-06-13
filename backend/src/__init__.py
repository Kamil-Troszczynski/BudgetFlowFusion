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
    if "purchase_request" not in inspector.get_table_names():
        return

    purchase_request_columns = {
        column["name"] for column in inspector.get_columns("purchase_request")
    }
    with engine.begin() as connection:
        if "project_budget_id" not in purchase_request_columns:
            connection.execute(text(
                "ALTER TABLE purchase_request ADD COLUMN project_budget_id INTEGER"
            ))

        connection.execute(text("""
            INSERT INTO project_budget (
                project_budget_name,
                total_budget,
                spent_money,
                association_budget_id,
                project_id
            )
            SELECT
                'Budżet projektu: ' || project.project_name,
                project.allocated_budget,
                project.allocated_budget - project.rest_of_budget,
                MIN(funding.association_budget_id),
                project.project_id
            FROM project
            JOIN funding ON funding.project_id = project.project_id
            LEFT JOIN project_budget ON project_budget.project_id = project.project_id
            WHERE project_budget.project_budget_id IS NULL
            GROUP BY project.project_id, project.project_name, project.allocated_budget, project.rest_of_budget
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
