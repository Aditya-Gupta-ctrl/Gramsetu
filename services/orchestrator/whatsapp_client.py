"""
WhatsApp Business API client for citizen notifications
Sends acknowledgements and status updates
"""
from twilio.rest import Client
from typing import Optional
from shared.config import get_settings
from shared.schemas import WhatsAppNotification
from shared.logging_config import logger

settings = get_settings()


class WhatsAppClient:
    """WhatsApp notification client using Twilio"""
    
    def __init__(self):
        self.client: Optional[Client] = None
    
    async def initialize(self):
        """Initialize Twilio client"""
        if settings.twilio_account_sid and settings.twilio_auth_token:
            self.client = Client(
                settings.twilio_account_sid,
                settings.twilio_auth_token
            )
            logger.info("WhatsApp client initialized (Twilio)")
        else:
            logger.warning("WhatsApp credentials not configured")
    
    async def send_notification(self, notification: WhatsAppNotification):
        """
        Send WhatsApp message to citizen
        
        Args:
            notification: WhatsAppNotification with recipient and message
        """
        if not self.client:
            logger.warning("WhatsApp client not initialized, skipping notification")
            return
        
        try:
            # Format phone number
            to_number = f"whatsapp:{notification.recipient_phone}"
            from_number = settings.twilio_whatsapp_number
            
            # Send message
            message = self.client.messages.create(
                body=notification.message_text,
                from_=from_number,
                to=to_number,
                media_url=[notification.image_url] if notification.image_url else None
            )
            
            logger.info(
                "WhatsApp notification sent",
                job_id=notification.job_id,
                recipient=notification.recipient_phone,
                message_sid=message.sid
            )
            
        except Exception as e:
            logger.error(f"WhatsApp notification failed: {str(e)}")
            # Don't raise - notification failure shouldn't break the job
