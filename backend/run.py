import os
import uvicorn
from sqlalchemy import text
from sqlmodel import Session, select

from src import app
from src.routes.homepage import *
from src.relations import SQLModel, ProductCategory
from src import engine

@app.on_event("startup")
def on_startup():
    print("Inicjalizacja bazy danych i sprawdzanie schematu...")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing_data = session.exec(select(ProductCategory)).first()

        if not existing_data:
            print("Baza danych jest pusta! Wczytuję plik mockup_data.sql...")
            base_dir = os.path.dirname(os.path.abspath(__file__))
            sql_path = os.path.join(base_dir, "scripts", "mockup_data.sql")

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
                    print("="*60)
                    print(f"ZAPYTANIE, KTÓRE WYWALIŁO BAZĘ:\n{current_statement}\n")
                    print(f"DOKŁADNY BŁĄD OD POSTGRESQL:\n{e}")
                    print("="*60 + "\n")
            else:
                print(f"BŁĄD: Nie znaleziono pliku pod ścieżką: {sql_path}")
        else:
            print("Baza danych ma już dane. Pomijam plik .sql.")

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=8080, reload=True)