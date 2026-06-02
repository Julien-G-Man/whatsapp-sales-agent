import httpx
import base64
import uuid
from datetime import datetime, timedelta
from app.config import settings


class PaymentError(Exception):
    pass


class MoMoClient:
    BASE = "https://sandbox.momodeveloper.mtn.com"

    def __init__(self, sub_key: str, api_user: str, api_key: str, callback_url: str):
        self.sub_key = sub_key
        self.api_user = api_user
        self.api_key = api_key
        self.callback_url = callback_url
        self.env = settings.MOMO_ENVIRONMENT
        self._token: str | None = None
        self._expires: datetime | None = None

    async def _get_token(self) -> str:
        if self._token and self._expires and datetime.utcnow() < self._expires:
            return self._token
        creds = base64.b64encode(f"{self.api_user}:{self.api_key}".encode()).decode()
        async with httpx.AsyncClient() as client:
            result = await client.post(
                f"{self.BASE}/collection/token/",
                headers={
                    "Authorization": f"Basic {creds}",
                    "Ocp-Apim-Subscription-Key": self.sub_key,
                },
            )
            result.raise_for_status()
        data = result.json()
        self._token = data["access_token"]
        self._expires = datetime.utcnow() + timedelta(seconds=data["expires_in"] - 30)
        return self._token

    async def request_to_pay(
        self, amount: int, currency: str, external_id: str, payer_phone: str, payer_message: str
    ) -> str:
        token = await self._get_token()
        ref_id = str(uuid.uuid4())
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{self.BASE}/collection/v1_0/requesttopay",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Reference-Id": ref_id,
                    "X-Target-Environment": self.env,
                    "X-Callback-Url": self.callback_url,
                    "Ocp-Apim-Subscription-Key": self.sub_key,
                    "Content-Type": "application/json",
                },
                json={
                    "amount": str(amount),
                    "currency": currency,
                    "externalId": external_id,
                    "payer": {"partyIdType": "MSISDN", "partyId": payer_phone},
                    "payerMessage": payer_message,
                    "payeeNote": "Merci pour votre achat",
                },
            )
        # 202 = queued; real confirmation arrives via webhook callback
        if r.status_code == 202:
            return ref_id
        raise PaymentError(f"MoMo error {r.status_code}: {r.text}")

    async def get_payment_status(self, ref_id: str) -> dict:
        token = await self._get_token()
        async with httpx.AsyncClient() as c:
            r = await c.get(
                f"{self.BASE}/collection/v1_0/requesttopay/{ref_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Target-Environment": self.env,
                    "Ocp-Apim-Subscription-Key": self.sub_key,
                },
            )
            r.raise_for_status()
        return r.json()


momo_client = MoMoClient(
    sub_key=settings.MOMO_SUBSCRIPTION_KEY,
    api_user=settings.MOMO_API_USER,
    api_key=settings.MOMO_API_KEY,
    callback_url=settings.MOMO_CALLBACK_URL,
)