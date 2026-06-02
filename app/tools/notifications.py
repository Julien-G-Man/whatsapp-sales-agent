from app.config import settings
from app.services.whatsapp import whatsapp_client


BUSINESS_HOURS = {
    "open": "07:00",
    "close": "21:00",
    "timezone": "CAT (UTC+1)",
    "days": "Lundi – Samedi",
}


async def get_business_hours() -> dict:
    return {
        "business_name": settings.BUSINESS_NAME,
        "city": settings.BUSINESS_CITY,
        "hours": BUSINESS_HOURS,
    }


async def send_broadcast(message: str, phones: list) -> dict:
    sent = 0
    failed = 0
    for phone in phones:
        try:
            await whatsapp_client.send_message(to=phone, body=message)
            sent += 1
        except Exception:
            failed += 1
    return {"sent": sent, "failed": failed, "total": len(phones)}
