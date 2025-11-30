from typing import Optional

from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class Note(BaseModel):
    id: str
    title: str
    content: str
    created_at: str
    updated_at: str
    version: int

    class Config:
        from_attributes = True


class NoteVersion(BaseModel):
    id: str
    note_id: str
    title: str
    content: str
    version: int
    created_at: str

    class Config:
        from_attributes = True
