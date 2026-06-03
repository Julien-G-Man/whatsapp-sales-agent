"""
Meta Cloud API provider (production).
"""
import httpx
from fastapi import Request, Response
from app.services.whatsapp.base import WhatsAppProvider

GRAPH_URL = "https://graph.facebook.com/v19.0"


class MetaProvider(WhatsAppProvider):
    def __init__(self, access_token: str, phone_number_id: str, verify_token: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.verify_token = verify_token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def send_message(self, to: str, body: str) -> dict:
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{GRAPH_URL}/{self.phone_number_id}/messages",
                headers=self._headers(),
                json={
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": to,
                    "type": "text",
                    "text": {"preview_url": False, "body": body},
                },
            )
        return r.json()

    async def parse_incoming(self, request: Request) -> list[tuple[str, str]]:
        payload = await request.json()

        # Flatten entry → changes → messages into a single iterable (O(n))
        raw_messages = [
            msg
            for entry in payload.get("entry", [])
            for change in entry.get("changes", [])
            for msg in change.get("value", {}).get("messages", [])
        ]

        results: list[tuple[str, str]] = []
        for msg in raw_messages:
            sender = msg["from"]
            match msg.get("type"):
                case "text":
                    results.append((sender, msg["text"]["body"]))
                case "audio":
                    results.append((sender, "[Voice note reçu — fonctionnalité bientôt disponible]"))
        return results

    async def handle_verification(self, request: Request) -> Response:
        params = dict(request.query_params)
        if (
            params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == self.verify_token
        ):
            return Response(content=params["hub.challenge"], media_type="text/plain")
        return Response(content="Forbidden", status_code=403)
