import re
from sqlalchemy.orm import Session
from database import Message

URGENCY_KEYWORDS = [
    "urgent", "asap", "critical", "high priority", "important",
    "immediately", "emergency", "action required", "time sensitive"
]

class MessageService:
    @staticmethod
    def calculate_priority(subject: str, body: str, from_address: str) -> float:
        priority = 0.0

        # Check for urgency keywords (case-insensitive)
        combined_text = (subject + " " + body).lower()
        for keyword in URGENCY_KEYWORDS:
            if keyword in combined_text:
                priority += 2
                break

        # Check for all-caps subject (indicator of urgency)
        if subject and subject.isupper() and len(subject) > 3:
            priority += 1

        # Check sender patterns (VIP senders)
        vip_patterns = [r"boss@", r"ceo@", r"executive@", r"support@"]
        for pattern in vip_patterns:
            if re.search(pattern, from_address.lower()):
                priority += 1
                break

        # Cap priority at 5
        return min(priority, 5.0)

    @staticmethod
    def extract_action_items(body: str) -> list:
        action_patterns = [
            r"(?:TODO|TODO:)[:\s]+(.*?)(?:\n|$)",
            r"(?:Action|ACTION)[:\s]+(.*?)(?:\n|$)",
            r"(?:FYI|FYI:)[:\s]+(.*?)(?:\n|$)",
        ]

        items = []
        for pattern in action_patterns:
            matches = re.finditer(pattern, body, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                item_text = match.group(1).strip()
                if item_text and item_text not in items:
                    items.append(item_text)

        return items

    @staticmethod
    def create_message(
        db: Session,
        platform: str,
        from_address: str,
        subject: str,
        body: str
    ) -> Message:
        priority = MessageService.calculate_priority(subject, body, from_address)

        message = Message(
            platform=platform,
            from_address=from_address,
            subject=subject,
            body=body,
            priority=priority
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
