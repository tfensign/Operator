from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from database import get_db, Message
from services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])

class MessageCreate(BaseModel):
    platform: str
    from_address: str
    subject: Optional[str] = None
    body: str

class MessageResponse(BaseModel):
    id: int
    platform: str
    from_address: str
    subject: Optional[str]
    body: str
    priority: float
    created_at: datetime
    read_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True

class MessageUpdate(BaseModel):
    read_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@router.get("", response_model=List[MessageResponse])
async def list_messages(
    db: Session = Depends(get_db),
    platform: Optional[str] = None,
    priority_min: Optional[float] = Query(None),
    priority_max: Optional[float] = Query(None),
    skip: int = 0,
    limit: int = 100
):
    """List messages with optional filtering"""
    query = db.query(Message).filter(Message.deleted_at.is_(None))

    if platform:
        query = query.filter(Message.platform == platform)

    if priority_min is not None:
        query = query.filter(Message.priority >= priority_min)

    if priority_max is not None:
        query = query.filter(Message.priority <= priority_max)

    messages = query.order_by(desc(Message.priority), desc(Message.created_at)).offset(skip).limit(limit).all()
    return messages

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: int, db: Session = Depends(get_db)):
    """Get a single message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.patch("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    update: MessageUpdate,
    db: Session = Depends(get_db)
):
    """Mark message as read/unread or delete"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if update.read_at is not None:
        message.read_at = update.read_at

    if update.deleted_at is not None:
        message.deleted_at = update.deleted_at

    db.commit()
    db.refresh(message)
    return message

@router.post("/search")
async def search_messages(
    query_text: str,
    db: Session = Depends(get_db)
):
    """Full-text search on message body and subject"""
    search_pattern = f"%{query_text}%"
    results = db.query(Message).filter(
        and_(
            Message.deleted_at.is_(None),
            or_(
                Message.subject.ilike(search_pattern),
                Message.body.ilike(search_pattern)
            )
        )
    ).order_by(desc(Message.priority), desc(Message.created_at)).all()
    return results

@router.post("", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """Create a new message (via webhook)"""
    msg = MessageService.create_message(
        db,
        message.platform,
        message.from_address,
        message.subject or "",
        message.body
    )
    return msg
