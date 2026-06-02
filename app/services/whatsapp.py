import httpx
from app.config import settings


class WhatsAppClient:
    BASE = "https://waba.360dialog.io/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _headers(self) -> dict:
        return {
            "D360-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

    async def send_message(self, to: str, body: str) -> dict:
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self.BASE}/messages",
                headers=self._headers(),
                json={
                    "to": to,
                    "type": "text",
                    "text": {"body": body},
                },
            )
        return r.json()

    async def verify_webhook(self, token: str, challenge: str) -> str | None:
        if token == settings.WHATSAPP_VERIFY_TOKEN:
            return challenge
        return None


whatsapp_client = WhatsAppClient(api_key=settings.WHATSAPP_API_KEY)
