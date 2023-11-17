from fastapi import Depends, FastAPI, UploadFile
from sqlalchemy.orm import Session
from openai import OpenAI

from database import crud, models, schemas
from database.bootstrap import SessionLocal, engine
from settings import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/documents/", response_model=list[schemas.Document])
def read_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return documents


@app.post("/documents/", response_model=schemas.Document)
def create_document(document: schemas.DocumentCreate, db: Session = Depends(get_db)):
    return crud.create_document(db=db, document=document)


@app.post("/documents/upload")
async def upload_documents(files: list[UploadFile]):
    return crud.upload_documents(files)


@app.get("/test")
async def test():
    print('hello')
    client = OpenAI(api_key=settings.openai_api_key)
    assistant = client.beta.assistants.retrieve(assistant_id=settings.assistant_id)
    print(assistant)
    return {"assistant": assistant}
