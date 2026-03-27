import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings


class EmailService:
    """Email notification service"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        self.email_tracker = {}  # Track email count per user
    
    def send_document_processed_email(
        self,
        recipient_email: str,
        document_title: str,
        document_id: str
    ) -> bool:
        """Send email notification when document is processed"""
        
        # Check email limit
        if self.email_tracker.get(recipient_email, 0) >= 5:
            print(f"⚠️ Email limit reached for {recipient_email}")
            return False
        
        # Skip if email not configured
        if not self.smtp_user or not self.smtp_password:
            print("⚠️ Email not configured, skipping notification")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = f'Document Processed: {document_title}'
            msg['From'] = self.email_from
            msg['To'] = recipient_email
            
            # Email body
            body = f"""
Hi there,

Your document "{document_title}" has been successfully processed and added to the RAG system.

Document ID: {document_id}

You can now ask questions about this document in the chat interface.

If you have any questions, feel free to reach out!

Regards,
RAG AI Assistant 🤖
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            # Update tracker
            self.email_tracker[recipient_email] = self.email_tracker.get(recipient_email, 0) + 1
            
            print(f"✅ Email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False


# Global instance
email_service = EmailService()
