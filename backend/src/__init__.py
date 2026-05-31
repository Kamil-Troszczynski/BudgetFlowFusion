import os
from sqlmodel import SQLModel, Session, create_engine, select
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from src.relations import *

path = os.getenv('DATABASE_URL')
engine = create_engine(path, echo=False)

def prepare_database():
    print("Inicjalizacja bazy danych i sprawdzanie schematu...")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing_data = session.exec(select(ProductCategory)).first()

        if not existing_data:
            print("Baza danych jest pusta! Wczytuję plik mockup_data.sql...")

            src_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(src_dir)
            sql_path = os.path.join(backend_dir, "scripts", "mockup_data.sql")

            if os.path.exists(sql_path):
                with open(sql_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()

                sql_clean = ""
                for line in lines:
                    if not line.strip().startswith("--") and line.strip():
                        sql_clean += line

                statements = sql_clean.split(";")

                try:
                    current_statement = ""
                    for statement in statements:
                        if statement.strip():
                            current_statement = statement.strip()
                            session.execute(text(current_statement))
                    session.commit()
                    print("Zakończono automatyczne wgrywanie danych startowych!")
                except Exception as e:
                    session.rollback()
                    print("\n" + "="*60)
                    print("KRYTYCZNY BŁĄD W SKRYPCIE SQL!")
                    print(f"ZAPYTANIE:\n{current_statement}\nBŁĄD:\n{e}")
                    print("="*60 + "\n")
            else:
                print(f"BŁĄD: Nie znaleziono pliku pod ścieżką: {sql_path}")
        else:
            print("Baza danych ma już dane. Pomijam plik .sql.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    prepare_database()
    yield

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)