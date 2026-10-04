from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from database import get_db, Integration, Credential
from crypto import CryptoService

router = APIRouter(prefix="/integrations", tags=["integrations"])

class CredentialCreate(BaseModel):
    credential_type: str  # api_key, oauth_token, password, etc.
    value: str

class IntegrationSetup(BaseModel):
    credentials: Dict[str, str]  # credential_type -> value

class IntegrationResponse(BaseModel):
    id: int
    platform: str
    webhook_url: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(db: Session = Depends(get_db)):
    """List all integrations"""
    integrations = db.query(Integration).all()
    return integrations

@router.get("/{platform}", response_model=IntegrationResponse)
async def get_integration(platform: str, db: Session = Depends(get_db)):
    """Get a specific integration"""
    integration = db.query(Integration).filter(Integration.platform == platform).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration

@router.post("/{platform}")
async def setup_integration(
    platform: str,
    setup: IntegrationSetup,
    master_password: str,
    db: Session = Depends(get_db)
):
    """Add or update integration"""
    # Check if integration already exists
    integration = db.query(Integration).filter(Integration.platform == platform).first()

    if not integration:
        # Generate unique webhook URL
        webhook_url = f"http://localhost:3001/webhook/{platform}/{uuid.uuid4().hex[:16]}"
        integration = Integration(
            platform=platform,
            webhook_url=webhook_url,
            status="active"
        )
        db.add(integration)
        db.flush()  # Get the ID before committing

    # Store encrypted credentials
    for cred_type, value in setup.credentials.items():
        # Check if credential already exists
        existing = db.query(Credential).filter(
            Credential.platform == platform,
            Credential.credential_type == cred_type
        ).first()

        encrypted_value = CryptoService.encrypt_credential(master_password, value)

        if existing:
            existing.encrypted_value = encrypted_value
        else:
            new_cred = Credential(
                platform=platform,
                credential_type=cred_type,
                encrypted_value=encrypted_value
            )
            db.add(new_cred)

    db.commit()
    db.refresh(integration)

    return {
        "success": True,
        "integration": IntegrationResponse.from_orm(integration)
    }

@router.patch("/{platform}")
async def update_integration(
    platform: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update integration settings"""
    integration = db.query(Integration).filter(Integration.platform == platform).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    if status:
        integration.status = status

    db.commit()
    db.refresh(integration)

    return IntegrationResponse.from_orm(integration)

@router.delete("/{platform}")
async def delete_integration(platform: str, db: Session = Depends(get_db)):
    """Delete integration and its credentials"""
    integration = db.query(Integration).filter(Integration.platform == platform).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    # Delete associated credentials
    db.query(Credential).filter(Credential.platform == platform).delete()
    db.delete(integration)
    db.commit()

    return {"success": True, "message": f"Integration {platform} deleted"}
