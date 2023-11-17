from fastapi import UploadFile
from sqlalchemy.orm import Session
from openai import OpenAI
import time

from settings import Settings
from . import models, schemas


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

    files = client.beta.assistants.files.list(assistant_id=settings.assistant_id)
    file_ids = [file.id for file in files]

    for file in files:
        file = client.files.create(file=file.file.read(), purpose='assistants')
        db_item = models.Document(name=file.filename, external_id=file.id)
        db.add(db_item)
        db.commit()
        file_ids.append(file.id)

    client.beta.assistants.update(assistant_id=settings.assistant_id, file_ids=file_ids)
    assistant = client.beta.assistants.retrieve(assistant_id=settings.assistant_id)
    return {"assistant": assistant}


def chat(db: Session, message: str):
    settings = Settings()
    client = OpenAI(api_key=settings.openai_api_key)

    client.beta.threads.messages.create(thread_id=settings.thread_id, role="user", content=message)
    run = client.beta.threads.runs.create(
        thread_id=settings.thread_id,
        assistant_id=settings.assistant_id,
    )

    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=settings.thread_id,
            run_id=run.id
        )

        if run_status.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=settings.thread_id)
            return {"messages": messages}
        else:
            time.sleep(5)  # Sleep for 5 seconds before checking again
