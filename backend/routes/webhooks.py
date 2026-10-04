from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from services.message_service import MessageService

router = APIRouter(prefix="/webhook", tags=["webhooks"])

class GenericWebhook(BaseModel):
    from_address: str
    subject: Optional[str] = None
    body: str

@router.post("/email")
async def receive_email(
    payload: GenericWebhook,
    db: Session = Depends(get_db)
):
    """Receive incoming emails via webhook"""
    message = MessageService.create_message(
        db,
        "email",
        payload.from_address,
        payload.subject or "(no subject)",
        payload.body
    )
    return {
        "success": True,
        "message_id": message.id,
        "priority": message.priority
    }

@router.post("/slack")
async def receive_slack(
    payload: GenericWebhook,
    db: Session = Depends(get_db)
):
    """Receive Slack messages via webhook"""
    message = MessageService.create_message(
        db,
        "slack",
        payload.from_address,
        payload.subject or "Slack message",
        payload.body
    )
    return {
        "success": True,
        "message_id": message.id,
        "priority": message.priority
    }

@router.post("/sms")
async def receive_sms(
    payload: GenericWebhook,
    db: Session = Depends(get_db)
):
    """Receive SMS messages via webhook"""
    message = MessageService.create_message(
        db,
        "sms",
        payload.from_address,
        "(SMS)",
        payload.body
    )
    return {
        "success": True,
        "message_id": message.id,
        "priority": message.priority
    }

@router.post("/{platform}")
async def receive_generic(
    platform: str,
    payload: GenericWebhook,
    db: Session = Depends(get_db)
):
    """Generic webhook receiver for any platform"""
    message = MessageService.create_message(
        db,
        platform.lower(),
        payload.from_address,
        payload.subject or f"{platform} message",
        payload.body
    )
    return {
        "success": True,
        "message_id": message.id,
        "priority": message.priority
    }
