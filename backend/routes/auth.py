from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, User
from crypto import CryptoService

router = APIRouter(prefix="/auth", tags=["auth"])

class SetupRequest(BaseModel):
    master_password: str

class UnlockRequest(BaseModel):
    master_password: str

class UnlockResponse(BaseModel):
    success: bool

@router.post("/setup")
async def setup(request: SetupRequest, db: Session = Depends(get_db)):
    """Initialize the app with master password"""
    existing_user = db.query(User).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="App already initialized")

    password_hash = CryptoService.hash_password(request.master_password)
    user = User(master_password_hash=password_hash)
    db.add(user)
    db.commit()

    return {"success": True, "message": "Master password set"}

@router.post("/unlock", response_model=UnlockResponse)
async def unlock(request: UnlockRequest, db: Session = Depends(get_db)):
    """Verify master password"""
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=400, detail="App not initialized")

    if CryptoService.verify_password(request.master_password, user.master_password_hash):
        return UnlockResponse(success=True)
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@router.get("/initialized")
async def is_initialized(db: Session = Depends(get_db)):
    """Check if app has been initialized"""
    user = db.query(User).first()
    return {"initialized": user is not None}
