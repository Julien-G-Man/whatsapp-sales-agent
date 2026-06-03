"""WhatsApp provider factory.

Switch providers by setting WHATSAPP_PROVIDER in .env:
  WHATSAPP_PROVIDER=twilio   → Twilio Sandbox  (free, for testing)
  WHATSAPP_PROVIDER=meta     → Meta Cloud API  (production)
"""
from app.config import settings
from app.services.whatsapp.base import WhatsAppProvider
from app.services.whatsapp.meta import MetaProvider
from app.services.whatsapp.twilio import TwilioProvider


def _build() -> WhatsAppProvider:
    if settings.WHATSAPP_PROVIDER == "twilio":
        return TwilioProvider(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            from_number=settings.TWILIO_WHATSAPP_FROM,
        )
    # Default: Meta Cloud API
    return MetaProvider(
        access_token=settings.WHATSAPP_ACCESS_TOKEN,
        phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
        verify_token=settings.WHATSAPP_VERIFY_TOKEN,
    )


whatsapp_client: WhatsAppProvider = _build()
