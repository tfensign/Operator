from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from database import get_db, PendingSend, SentMessage
from services.sender_service import SenderService

router = APIRouter(prefix="/send", tags=["send"])

class DraftCreate(BaseModel):
    platform: str  # email, slack, sms
    to_address: str
    subject: Optional[str] = None
    body: str

class PendingSendResponse(BaseModel):
    id: int
    platform: str
    to_address: str
    subject: Optional[str]
    body: str
    created_at: datetime
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True

class SentMessageResponse(BaseModel):
    id: int
    platform: str
    to_address: str
    subject: Optional[str]
    body: str
    sent_at: datetime
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True

class ApproveRequest(BaseModel):
    master_password: str

@router.post("/draft", response_model=PendingSendResponse)
async def create_draft(
    draft: DraftCreate,
    db: Session = Depends(get_db)
):
    """Create a draft message for approval"""
    pending = PendingSend(
        platform=draft.platform,
        to_address=draft.to_address,
        subject=draft.subject,
        body=draft.body
    )
    db.add(pending)
    db.commit()
    db.refresh(pending)
    return pending

@router.get("/pending", response_model=List[PendingSendResponse])
async def list_pending(db: Session = Depends(get_db)):
    """List all messages pending approval"""
    pending = db.query(PendingSend).filter(
        PendingSend.approved_at.is_(None)
    ).order_by(PendingSend.created_at.desc()).all()
    return pending

@router.post("/{pending_id}/approve", response_model=SentMessageResponse)
async def approve_and_send(
    pending_id: int,
    request: ApproveRequest,
    db: Session = Depends(get_db)
):
    """Approve and send a pending message"""
    pending = db.query(PendingSend).filter(PendingSend.id == pending_id).first()
    if not pending:
        raise HTTPException(status_code=404, detail="Pending message not found")

    success = SenderService.approve_and_send(db, pending_id, request.master_password)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send message")

    # Fetch the sent message
    sent = db.query(SentMessage).filter(
        SentMessage.to_address == pending.to_address,
        SentMessage.platform == pending.platform
    ).order_by(SentMessage.sent_at.desc()).first()

    return sent

@router.post("/{pending_id}/reject")
async def reject(
    pending_id: int,
    db: Session = Depends(get_db)
):
    """Reject and delete a pending message"""
    pending = db.query(PendingSend).filter(PendingSend.id == pending_id).first()
    if not pending:
        raise HTTPException(status_code=404, detail="Pending message not found")

    db.delete(pending)
    db.commit()

    return {"success": True, "message": "Message rejected"}

@router.get("/history", response_model=List[SentMessageResponse])
async def sent_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get history of sent messages"""
    sent = db.query(SentMessage).order_by(SentMessage.sent_at.desc()).limit(limit).all()
    return sent
