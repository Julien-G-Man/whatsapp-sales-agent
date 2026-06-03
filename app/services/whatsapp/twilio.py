"""Twilio WhatsApp Sandbox provider (testing).

Setup:
  1. twilio.com → sign up (free) → Console → Messaging → Try it out → WhatsApp
  2. The sandbox number is shown (e.g. +14155238886). Save it as TWILIO_WHATSAPP_FROM.
  3. Each tester must WhatsApp that number with the join phrase shown once
     (e.g. "join bright-tiger") — one-time setup per device.
  4. Webhook URL: https://<your-app>.onrender.com/webhook/whatsapp
     (set under Sandbox Settings → "When a message comes in")
  5. No GET verification needed — leave the GET endpoint alone.

Env vars needed:
  TWILIO_ACCOUNT_SID
  TWILIO_AUTH_TOKEN
  TWILIO_WHATSAPP_FROM   e.g. +14155238886
"""
import httpx
from fastapi import Request, Response
from app.services.whatsapp.base import WhatsAppProvider

TWILIO_API = "https://api.twilio.com/2010-04-01"


class TwilioProvider(WhatsAppProvider):
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        # Accept with or without the whatsapp: prefix
        self.from_wa = (
            from_number if from_number.startswith("whatsapp:")
            else f"whatsapp:{from_number}"
        )

    async def send_message(self, to: str, body: str) -> dict:
        to_wa = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{TWILIO_API}/Accounts/{self.account_sid}/Messages.json",
                auth=(self.account_sid, self.auth_token),
                data={"From": self.from_wa, "To": to_wa, "Body": body},
            )
        return r.json()

    async def parse_incoming(self, request: Request) -> list[tuple[str, str]]:
        # Twilio sends form-encoded data, not JSON
        form = await request.form()
        raw_from = str(form.get("From", ""))
        body = str(form.get("Body", "")).strip()
        # Strip the "whatsapp:" prefix so the rest of the app sees plain numbers
        sender = raw_from.replace("whatsapp:", "")
        if sender and body:
            return [(sender, body)]
        return []

    async def handle_verification(self, request: Request) -> Response:
        # Twilio doesn't use Meta's hub.challenge handshake — just return 200
        return Response(content="OK", status_code=200)
