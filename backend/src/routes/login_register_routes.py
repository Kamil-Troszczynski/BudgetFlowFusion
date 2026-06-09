from src.relations import *
from src import get_session, app
from sqlmodel import Session, select
from fastapi import Depends
from pydantic import BaseModel
from fastapi import HTTPException



class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    surname: str
    login: str
    password: str
    position: str
    is_in_sap: bool
    association_name: str
    is_treasurer: bool = False


@app.post("/api/login")
def login_user(credentials: LoginRequest, session: Session = Depends(get_session)):
    statement = select(Student).where(Student.login == credentials.email)
    user = session.exec(statement).first()

    if not user or user.password_hash != credentials.password:
        raise HTTPException(status_code = 401, detail = "Nieprawidłowy email lub hasło")

    return {
        "id": user.student_id,
        "firstName": user.name,
        "lastName": user.surname,
        "email": user.login,
        "circleName": user.association.association_name if user.association else "Brak koła",
        "association_id": user.association_id,
        "position": user.position,
        "inSAP": user.is_in_sap,
        "project_finance_manager_id": user.project_finance_manager_id,
        "role": "treasurer" if user.project_finance_manager_id else "member"
    }


@app.post("/api/register")
def sign_up(credentials: RegisterRequest, session: Session = Depends(get_session)):
    existing_student = session.exec(
        select(Student).where(Student.login == credentials.login)
    ).first()
    if existing_student:
        raise HTTPException(status_code = 401, detail = "Podany e-mail jest już zajęty")

    association = session.exec(select(Association).where(Association.association_name == credentials.association_name)).first()
    if not association:
        association = Association(association_name=credentials.association_name)
        session.add(association)
        session.commit()
        session.refresh(association)

    finance_manager = None
    if credentials.is_treasurer:
        finance_manager = ProjectFinanceManager(
            login=credentials.login,
            password_hash=credentials.password,
            access=True
        )
        session.add(finance_manager)
        session.commit()
        session.refresh(finance_manager)

    new_student = Student(
        name=credentials.name,
        surname=credentials.surname,
        login=credentials.login,
        password_hash=credentials.password,
        position=credentials.position,
        is_in_sap=credentials.is_in_sap,
        association_name=association.association_name,
        project_finance_manager_id=finance_manager.project_finance_manager_id if finance_manager else None
    )

    session.add(new_student)
    session.commit()
    session.refresh(new_student)

    return new_student
