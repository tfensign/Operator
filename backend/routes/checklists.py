from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from database import get_db, Checklist, ChecklistItem
from services.checklist_service import ChecklistService

router = APIRouter(prefix="/checklists", tags=["checklists"])

class ChecklistItemCreate(BaseModel):
    text: str

class ChecklistItemResponse(BaseModel):
    id: int
    checklist_id: int
    text: str
    completed_at: Optional[datetime]
    source_message_id: Optional[int]

    class Config:
        from_attributes = True

class ChecklistCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ChecklistResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    items: List[ChecklistItemResponse] = []

    class Config:
        from_attributes = True

@router.get("", response_model=List[ChecklistResponse])
async def list_checklists(db: Session = Depends(get_db)):
    """List all checklists"""
    checklists = db.query(Checklist).order_by(Checklist.created_at.desc()).all()
    return checklists

@router.get("/{checklist_id}", response_model=ChecklistResponse)
async def get_checklist(checklist_id: int, db: Session = Depends(get_db)):
    """Get a single checklist with items"""
    checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return checklist

@router.post("", response_model=ChecklistResponse)
async def create_checklist(
    checklist: ChecklistCreate,
    db: Session = Depends(get_db)
):
    """Create a new checklist"""
    new_checklist = ChecklistService.create_checklist(
        db,
        checklist.title,
        checklist.description
    )
    return new_checklist

@router.post("/from-message/{message_id}", response_model=ChecklistResponse)
async def create_from_message(
    message_id: int,
    title: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create checklist from message (auto-extract action items)"""
    checklist = ChecklistService.create_checklist_from_message(
        db,
        message_id,
        title
    )
    if not checklist:
        raise HTTPException(status_code=404, detail="Message not found")
    return checklist

@router.post("/{checklist_id}/items", response_model=ChecklistItemResponse)
async def add_item(
    checklist_id: int,
    item: ChecklistItemCreate,
    db: Session = Depends(get_db)
):
    """Add item to checklist"""
    checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    new_item = ChecklistService.add_item(db, checklist_id, item.text)
    return new_item

@router.patch("/{checklist_id}/items/{item_id}")
async def mark_item_complete(
    checklist_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Mark checklist item as complete"""
    item = db.query(ChecklistItem).filter(
        ChecklistItem.id == item_id,
        ChecklistItem.checklist_id == checklist_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_item = ChecklistService.mark_item_complete(db, item_id)
    return updated_item
