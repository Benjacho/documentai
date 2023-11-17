from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True


class DocumentBase(BaseModel):
    name: str
    embed_content: str
    path: str


class DocumentCreate(DocumentBase):
    name: str
    embed_content: str
    path: str


class Document(DocumentBase):
    id: int
    name: str
    embed_content: str
    path: str

    class Config:
        orm_mode = True
