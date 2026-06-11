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
    student = session.exec(select(Student).where(Student.login == credentials.email)).first()

    if student:
        if student.password_hash != credentials.password:
            raise HTTPException(status_code=401, detail="Nieprawidłowy email lub hasło")
        return {
            "id": student.student_id,
            "firstName": student.name,
            "lastName": student.surname,
            "email": student.login,
            "circleName": student.association.association_name if student.association else "Brak koła",
            "association_id": student.association_id,
            "position": student.position,
            "inSAP": student.is_in_sap,
            "project_finance_manager_id": student.project_finance_manager_id,
            "role": "treasurer" if student.project_finance_manager_id else "member"
        }

    pfm = session.exec(select(ProjectFinanceManager).where(ProjectFinanceManager.login == credentials.email)).first()

    if not pfm or pfm.password_hash != credentials.password:
        raise HTTPException(status_code=401, detail="Nieprawidłowy email lub hasło")

    linked_student = pfm.student
    return {
        "id": linked_student.student_id if linked_student else None,
        "firstName": linked_student.name if linked_student else "",
        "lastName": linked_student.surname if linked_student else "",
        "email": pfm.login,
        "circleName": linked_student.association.association_name if linked_student and linked_student.association else "Brak koła",
        "association_id": linked_student.association_id if linked_student else None,
        "position": linked_student.position if linked_student else "",
        "inSAP": linked_student.is_in_sap if linked_student else False,
        "project_finance_manager_id": pfm.project_finance_manager_id,
        "role": "treasurer"
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
        association_id=association.association_id,
        project_finance_manager_id=finance_manager.project_finance_manager_id if finance_manager else None
    )

    session.add(new_student)
    session.commit()
    session.refresh(new_student)

    return new_student
