from sqlalchemy.orm import Session
from database import Checklist, ChecklistItem, Message
from services.message_service import MessageService

class ChecklistService:
    @staticmethod
    def create_checklist(
        db: Session,
        title: str,
        description: str = None
    ) -> Checklist:
        checklist = Checklist(
            title=title,
            description=description
        )
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
        return checklist

    @staticmethod
    def create_checklist_from_message(
        db: Session,
        message_id: int,
        title: str = None
    ) -> Checklist:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return None

        # Extract action items from message body
        action_items = MessageService.extract_action_items(message.body)

        # Create checklist with message subject as title if not provided
        if not title:
            title = f"Actions from: {message.subject or message.from_address}"

        checklist = ChecklistService.create_checklist(db, title)

        # Add extracted items to checklist
        for item_text in action_items:
            item = ChecklistItem(
                checklist_id=checklist.id,
                text=item_text,
                source_message_id=message_id
            )
            db.add(item)

        db.commit()
        return checklist

    @staticmethod
    def add_item(
        db: Session,
        checklist_id: int,
        text: str
    ) -> ChecklistItem:
        item = ChecklistItem(
            checklist_id=checklist_id,
            text=text
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def mark_item_complete(
        db: Session,
        item_id: int
    ) -> ChecklistItem:
        from datetime import datetime
        item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
        if item:
            item.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(item)
        return item
