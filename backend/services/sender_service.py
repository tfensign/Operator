import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from database import SentMessage, PendingSend, Credential
from crypto import CryptoService
from datetime import datetime, timezone

class SenderService:
    @staticmethod
    def send_email(
        to_address: str,
        subject: str,
        body: str,
        from_email: str,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str
    ) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_address
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    def send_slack_message(
        to_user_id: str,
        body: str,
        bot_token: str
    ) -> bool:
        try:
            from slack_sdk import WebClient
            client = WebClient(token=bot_token)
            client.chat_postMessage(
                channel=to_user_id,
                text=body
            )
            return True
        except Exception as e:
            print(f"Error sending Slack message: {e}")
            return False

    @staticmethod
    def send_sms(
        to_phone: str,
        body: str,
        twilio_sid: str,
        twilio_token: str,
        from_phone: str
    ) -> bool:
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            client.messages.create(
                to=to_phone,
                from_=from_phone,
                body=body
            )
            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    @staticmethod
    def approve_and_send(
        db: Session,
        pending_id: int,
        master_password: str
    ) -> bool:
        pending = db.query(PendingSend).filter(PendingSend.id == pending_id).first()
        if not pending:
            return False

        platform = pending.platform.lower()

        try:
            # Get credentials from database (encrypted)
            creds = db.query(Credential).filter(
                Credential.platform == platform
            ).all()

            if not creds:
                return False

            success = False

            if platform == "email":
                # Decrypt email credentials
                smtp_creds = {c.credential_type: CryptoService.decrypt_credential(master_password, c.encrypted_value) for c in creds}
                # For MVP, we'll need SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD in credentials
                # This is a simplified approach - in production you'd validate and parse these carefully
                success = SenderService.send_email(
                    to_address=pending.to_address,
                    subject=pending.subject or "",
                    body=pending.body,
                    from_email=smtp_creds.get("smtp_user", ""),
                    smtp_host=smtp_creds.get("smtp_host", "smtp.gmail.com"),
                    smtp_port=int(smtp_creds.get("smtp_port", 587)),
                    smtp_user=smtp_creds.get("smtp_user", ""),
                    smtp_password=smtp_creds.get("smtp_password", "")
                )

            elif platform == "slack":
                # Decrypt Slack token
                slack_cred = next((c for c in creds if c.credential_type == "bot_token"), None)
                if slack_cred:
                    bot_token = CryptoService.decrypt_credential(master_password, slack_cred.encrypted_value)
                    success = SenderService.send_slack_message(
                        to_user_id=pending.to_address,
                        body=pending.body,
                        bot_token=bot_token
                    )

            elif platform == "sms":
                # Decrypt Twilio credentials
                twilio_creds = {c.credential_type: CryptoService.decrypt_credential(master_password, c.encrypted_value) for c in creds}
                success = SenderService.send_sms(
                    to_phone=pending.to_address,
                    body=pending.body,
                    twilio_sid=twilio_creds.get("twilio_sid", ""),
                    twilio_token=twilio_creds.get("twilio_token", ""),
                    from_phone=twilio_creds.get("from_phone", "")
                )

            if success:
                # Create sent message record
                sent_msg = SentMessage(
                    platform=pending.platform,
                    to_address=pending.to_address,
                    subject=pending.subject,
                    body=pending.body,
                    approved_at=datetime.now(timezone.utc)
                )
                db.add(sent_msg)

                # Delete from pending
                db.delete(pending)
                db.commit()
                return True

            return False

        except Exception as e:
            print(f"Error in approve_and_send: {e}")
            return False
