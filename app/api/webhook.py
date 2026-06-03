import traceback
from fastapi import APIRouter, Request, BackgroundTasks, Response
from app.agent.core import run_agent, save_message
from app.services.whatsapp import whatsapp_client

router = APIRouter()


@router.get("/webhook/whatsapp")
async def verify_webhook(request: Request) -> Response:
    """Delegate verification handshake to the active provider."""
    return await whatsapp_client.handle_verification(request)


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, bg: BackgroundTasks):
    """Receive messages. Returns 200 immediately; agent runs in background."""
    messages = await whatsapp_client.parse_incoming(request)
    for sender, text in messages:
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
