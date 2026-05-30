from sqlmodel import SQLModel, Session, create_engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from src.relations import *
import os


path = os.getenv('DATABASE_URL')
engine = create_engine(path, echo = True)


MOCKUP_DATA_FILEPATH = "scripts/mockup_data.sql"


def prepare_database(mockup_data_filepath: str):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        try:
            with open(mockup_data_filepath, 'r') as file:
                sql_instructions = text(file.read())
            session.exec(sql_instructions)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"SQL instructions failed - exception {e}")


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