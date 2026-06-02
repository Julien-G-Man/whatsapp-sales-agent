import traceback
from fastapi import APIRouter, Request, BackgroundTasks, Response
from app.agent.core import run_agent, save_message
from app.services.whatsapp import whatsapp_client
from app.config import settings

router = APIRouter()


@router.get("/webhook/whatsapp")
async def verify_webhook(request: Request):
    """360dialog/Meta webhook verification handshake."""
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, bg: BackgroundTasks):
    """Receive incoming WhatsApp messages from 360dialog.
    Must return 200 fast — heavy work goes to background task."""
    payload = await request.json()
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for message in change.get("value", {}).get("messages", []):
                sender = message["from"]
                msg_type = message.get("type")

                if msg_type == "text":
                    text = message["text"]["body"]
                elif msg_type == "audio":
                    text = "[Voice note reçu — fonctionnalité bientôt disponible]"
                else:
                    continue

                bg.add_task(process_message, sender, text)

    return {"status": "ok"}


async def process_message(sender: str, text: str) -> None:
    try:
        response = await run_agent(sender, text)
        await whatsapp_client.send_message(to=sender, body=response)
        await save_message(sender, "user", text)
        await save_message(sender, "assistant", response)
    except Exception as e:
        print(f"[ERROR] process_message({sender}): {e}\n{traceback.format_exc()}")
        await whatsapp_client.send_message(
            to=sender,
            body="Désolé, une erreur s'est produite. Veuillez réessayer.",
        )
