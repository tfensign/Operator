from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    master_password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)  # email, slack, sms
    from_address = Column(String, nullable=False)
    subject = Column(String)
    body = Column(Text, nullable=False)
    priority = Column(Float, default=0)  # 0-5
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

class Checklist(Base):
    __tablename__ = "checklists"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    id = Column(Integer, primary_key=True)
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    text = Column(String, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    source_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)

class Credential(Base):
    __tablename__ = "credentials"
    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)  # email, slack, sms, etc.
    credential_type = Column(String, nullable=False)  # api_key, oauth_token, password
    encrypted_value = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Integration(Base):
    __tablename__ = "integrations"
    id = Column(Integer, primary_key=True)
    platform = Column(String, unique=True, nullable=False)
    webhook_url = Column(String)
    status = Column(String, default="inactive")  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)

class PendingSend(Base):
    __tablename__ = "pending_sends"
    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    subject = Column(String)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

class SentMessage(Base):
    __tablename__ = "sent_messages"
    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    subject = Column(String)
    body = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
