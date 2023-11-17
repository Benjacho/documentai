from fastapi import UploadFile
from sqlalchemy.orm import Session
from openai import OpenAI

from settings import Settings
from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def create_document(db: Session, document: schemas.DocumentCreate):
    db_document = models.Document(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int):
    return db.query(models.Document).filter(models.Document.id == document_id).first()


def get_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Document).offset(skip).limit(limit).all()


def upload_documents(db: Session, files: list[UploadFile]):
    settings = Settings()
    client = OpenAI(api_key=settings.openai_api_key)

    file_ids = client.beta.assistants.retrieve(assistant_id=settings.assistant_id).file_ids

    for file in files:
        file = client.files.create(file=file.file.read(), purpose='assistants')
        db_item = models.Document(name=file.filename, external_id=file.id)
        db.add(db_item)
        db.commit()
        file_ids.append(file.id)

    client.beta.assistants.update(assistant_id=settings.assistant_id, file_ids=file_ids)
    assistant = client.beta.assistants.retrieve(assistant_id=settings.assistant_id)
    return {"assistant": assistant}
