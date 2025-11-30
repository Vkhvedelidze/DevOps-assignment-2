import uuid
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models, schemas


def get_note(db: Session, note_id: str):
    return db.query(models.NoteDB).filter(models.NoteDB.id == note_id).first()


def get_notes(db: Session, search: str = None):
    query = db.query(models.NoteDB)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            or_(
                models.NoteDB.title.ilike(search_lower),
                models.NoteDB.content.ilike(search_lower),
            )
        )
    return query.all()


def create_note(db: Session, note: schemas.NoteCreate):
    note_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    # Create DB object
    new_note_db = models.NoteDB(
        id=note_id,
        title=note.title,
        content=note.content,
        created_at=now,
        updated_at=now,
        version=1,
    )

    # Create version DB object
    version_id = str(uuid.uuid4())
    new_version_db = models.NoteVersionDB(
        id=version_id,
        note_id=note_id,
        title=note.title,
        content=note.content,
        version=1,
        created_at=now,
    )

    try:
        db.add(new_note_db)
        db.add(new_version_db)
        db.commit()
        db.refresh(new_note_db)
        return new_note_db
    except Exception as e:
        db.rollback()
        raise e


def update_note(db: Session, note_id: str, note_update: schemas.NoteUpdate):
    existing_note = get_note(db, note_id)
    if not existing_note:
        return None

    new_version = existing_note.version + 1
    now = datetime.now().isoformat()

    # Create new version record
    version_id = str(uuid.uuid4())
    new_version_db = models.NoteVersionDB(
        id=version_id,
        note_id=note_id,
        title=note_update.title or existing_note.title,
        content=note_update.content or existing_note.content,
        version=new_version,
        created_at=now,
    )

    # Update the note
    if note_update.title is not None:
        existing_note.title = note_update.title
    if note_update.content is not None:
        existing_note.content = note_update.content

    existing_note.updated_at = now
    existing_note.version = new_version

    try:
        db.add(new_version_db)
        db.commit()
        db.refresh(existing_note)
        return existing_note
    except Exception as e:
        db.rollback()
        raise e


def delete_note(db: Session, note_id: str):
    note = get_note(db, note_id)
    if note:
        try:
            db.delete(note)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
    return False


def get_note_versions(db: Session, note_id: str):
    return (
        db.query(models.NoteVersionDB)
        .filter(models.NoteVersionDB.note_id == note_id)
        .order_by(models.NoteVersionDB.version.desc())
        .all()
    )


def restore_note_version(db: Session, note_id: str, version_id: str):
    note = get_note(db, note_id)
    if not note:
        return None, "Note not found"

    version_data = (
        db.query(models.NoteVersionDB)
        .filter(models.NoteVersionDB.id == version_id)
        .first()
    )
    if not version_data:
        return None, "Version not found"

    if version_data.note_id != note_id:
        return None, "Version does not belong to this note"

    new_version = note.version + 1
    now = datetime.now().isoformat()

    # Create version record for the restore action
    restore_version_id = str(uuid.uuid4())
    restore_version_db = models.NoteVersionDB(
        id=restore_version_id,
        note_id=note_id,
        title=version_data.title,
        content=version_data.content,
        version=new_version,
        created_at=now,
    )

    # Update the note with restored content
    note.title = version_data.title
    note.content = version_data.content
    note.updated_at = now
    note.version = new_version

    try:
        db.add(restore_version_db)
        db.commit()
        db.refresh(note)
        return note, None
    except Exception as e:
        db.rollback()
        raise e
