import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import crud, schemas
from .config import TEMPLATES_DIR
from .database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# API Routes
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main notes app interface"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/api/notes/", response_model=schemas.Note)
async def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    """Create a new note"""
    try:
        return crud.create_note(db=db, note=note)
    except Exception as e:
        logger.error(f"Error creating note: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/notes/", response_model=List[schemas.Note])
async def get_notes(
    search: Optional[str] = Query(None, min_length=1), db: Session = Depends(get_db)
):
    """Get all notes, optionally filtered by search term"""
    return crud.get_notes(db=db, search=search)


@router.get("/api/notes/{note_id}", response_model=schemas.Note)
async def get_note(note_id: str, db: Session = Depends(get_db)):
    """Get a specific note"""
    note = crud.get_note(db=db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/api/notes/{note_id}", response_model=schemas.Note)
async def update_note(
    note_id: str, note_update: schemas.NoteUpdate, db: Session = Depends(get_db)
):
    """Update a note and create a new version"""
    updated_note = crud.update_note(db=db, note_id=note_id, note_update=note_update)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note


@router.delete("/api/notes/{note_id}")
async def delete_note(note_id: str, db: Session = Depends(get_db)):
    """Delete a note"""
    success = crud.delete_note(db=db, note_id=note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}


@router.get("/api/notes/{note_id}/versions", response_model=List[schemas.NoteVersion])
async def get_note_versions(note_id: str, db: Session = Depends(get_db)):
    """Get all versions of a specific note"""
    note = crud.get_note(db=db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return crud.get_note_versions(db=db, note_id=note_id)


@router.post("/api/notes/{note_id}/restore/{version_id}", response_model=schemas.Note)
async def restore_note_version(
    note_id: str, version_id: str, db: Session = Depends(get_db)
):
    """Restore a note to a specific version"""
    note, error = crud.restore_note_version(
        db=db, note_id=note_id, version_id=version_id
    )
    if error:
        if error == "Note not found":
            raise HTTPException(status_code=404, detail="Note not found")
        elif error == "Version not found":
            raise HTTPException(status_code=404, detail="Version not found")
        elif error == "Version does not belong to this note":
            raise HTTPException(
                status_code=400, detail="Version does not belong to this note"
            )
        else:
            raise HTTPException(status_code=500, detail=error)
    return note
