from fastapi import APIRouter, Request
from app.config import settings
from app.services.whatsapp import whatsapp_client
from app.tools.orders import get_order_by_momo_ref, update_order_status
from app.tools.payments import confirm_payment, fail_payment, decrement_inventory

router = APIRouter()


@router.post("/webhook/momo")
async def momo_webhook(request: Request):
    """MTN MoMo payment callback. Called by MTN when a payment is SUCCESSFUL or FAILED."""
    payload = await request.json()
    await handle_momo_callback(payload)
    return {"status": "ok"}


async def handle_momo_callback(payload: dict) -> None:
    ref = payload.get("externalId")
    status = payload.get("status")  # 'SUCCESSFUL' | 'FAILED'

    if not ref:
        return

    order = await get_order_by_momo_ref(ref)
    if not order:
        return

    if status == "SUCCESSFUL":
        await update_order_status(order.id, "paid")
        await confirm_payment(ref)
        await decrement_inventory(order.items or [])

        await whatsapp_client.send_message(
            to=order.customer_phone,
            body=(
                f"✅ Paiement reçu ! Merci.\n"
                f"Commande #{order.id} confirmée — {order.total_xaf:,} XAF.\n"
                f"Nous préparons votre commande."
            ),
        )
        await whatsapp_client.send_message(
            to=settings.MERCHANT_PHONE,
            body=(
                f"💰 Paiement reçu : {order.total_xaf:,} XAF\n"
                f"Commande #{order.id} — Client : {order.customer_phone}"
            ),
        )

    elif status == "FAILED":
        await update_order_status(order.id, "payment_failed")
        await fail_payment(ref)

        await whatsapp_client.send_message(
            to=order.customer_phone,
            body=(
                "❌ Le paiement a échoué. Voulez-vous réessayer ?\n"
                "Répondez 'oui' et je relancerai la demande."
            ),
        )
