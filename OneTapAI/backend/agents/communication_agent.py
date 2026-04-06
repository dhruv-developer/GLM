"""
Communication Agent for ZIEL-MAS
Handles sending messages via email, WhatsApp, SMS
"""

import aiosmtplib
from email.message import EmailMessage
from typing import Dict, Any, List
from loguru import logger
import os

from backend.agents.base_agent import BaseAgent


class CommunicationAgent(BaseAgent):
    """
    Communication Agent - Sends messages through various channels
    Supports Email, WhatsApp, and SMS
    """

    def __init__(self):
        super().__init__("Communication Agent", "communication")

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a communication action"""
        try:
            if action == "send_email":
                return await self._send_email(parameters)
            elif action == "send_whatsapp":
                return await self._send_whatsapp(parameters)
            elif action == "send_sms":
                return await self._send_sms(parameters)
            elif action == "send_message":
                return await self._send_message(parameters)
            else:
                return self._create_response(
                    status="failed",
                    error=f"Unknown action: {action}"
                )

        except Exception as e:
            return await self.handle_error(action, e)

    async def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email"""
        to = params.get("to", [])
        subject = params.get("subject", "")
        body = params.get("body", "")
        attachments = params.get("attachments", [])

        if not to or not subject:
            return self._create_response(
                status="failed",
                error="Recipients and subject are required"
            )

        logger.info(f"Sending email to {to}")

        # Create email message
        message = EmailMessage()
        message["From"] = os.getenv("SMTP_USER", "noreply@zielmas.ai")
        message["To"] = ", ".join(to)
        message["Subject"] = subject
        message.set_content(body)

        # Send email
        try:
            # Mock implementation for development
            # In production, use actual SMTP
            # await aiosmtplib.send(
            #     message,
            #     hostname=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            #     port=int(os.getenv("SMTP_PORT", "587")),
            #     username=os.getenv("SMTP_USER"),
            #     password=os.getenv("SMTP_PASSWORD"),
            #     start_tls=True
            # )

            logger.info(f"Email sent successfully to {to}")

            return self._create_response(
                status="success",
                output={
                    "recipients": to,
                    "subject": subject,
                    "message_id": "email_123456",
                    "sent_at": "2024-01-01T00:00:00Z"
                }
            )

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return self._create_response(
                status="failed",
                error=f"Failed to send email: {str(e)}"
            )

    async def _send_whatsapp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a WhatsApp message"""
        to = params.get("to")
        message = params.get("message")

        if not to or not message:
            return self._create_response(
                status="failed",
                error="Recipient and message are required"
            )

        logger.info(f"Sending WhatsApp message to {to}")

        # Mock implementation - would use Twilio or similar
        # from twilio.rest import Client
        # client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        # message = client.messages.create(
        #     from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
        #     body=message,
        #     to=f"whatsapp:{to}"
        # )

        return self._create_response(
            status="success",
            output={
                "recipient": to,
                "message": message,
                "message_id": "wa_123456",
                "sent_at": "2024-01-01T00:00:00Z"
            }
        )

    async def _send_sms(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an SMS message"""
        to = params.get("to")
        message = params.get("message")

        if not to or not message:
            return self._create_response(
                status="failed",
                error="Recipient and message are required"
            )

        logger.info(f"Sending SMS to {to}")

        # Mock implementation - would use Twilio
        return self._create_response(
            status="success",
            output={
                "recipient": to,
                "message": message,
                "message_id": "sms_123456",
                "sent_at": "2024-01-01T00:00:00Z"
            }
        )

    async def _send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message (auto-detect channel)"""
        recipient = params.get("recipient")
        message = params.get("message")

        if not recipient or not message:
            return self._create_response(
                status="failed",
                error="Recipient and message are required"
            )

        # Auto-detect channel based on recipient format
        if "@" in recipient:
            # Email
            return await self._send_email({
                "to": [recipient],
                "subject": params.get("subject", "Message"),
                "body": message
            })
        elif recipient.startswith("+"):
            # Phone number - default to WhatsApp
            return await self._send_whatsapp({
                "to": recipient,
                "message": message
            })
        else:
            return self._create_response(
                status="failed",
                error="Cannot determine message channel from recipient"
            )
