from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


# SQLAlchemy Models (DB)
class NoteDB(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
    version = Column(Integer)

    versions = relationship(
        "NoteVersionDB", back_populates="note", cascade="all, delete-orphan"
    )


class NoteVersionDB(Base):
    __tablename__ = "note_versions"

    id = Column(String, primary_key=True, index=True)
    note_id = Column(String, ForeignKey("notes.id"))
    title = Column(String)
    content = Column(String)
    version = Column(Integer)
    created_at = Column(String)

    note = relationship("NoteDB", back_populates="versions")


# Pydantic models moved to schemas.py
