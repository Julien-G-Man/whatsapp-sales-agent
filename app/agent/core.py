import json
from anthropic import AsyncAnthropic
from sqlalchemy import select
from app.config import settings
from app.agent.prompts import CUSTOMER_SYSTEM, MERCHANT_SYSTEM
from app.agent.router import get_tools, is_merchant
from app.db.models import ConversationMessage
from app.db.session import AsyncSessionLocal
from app.tools.inventory import query_inventory, update_inventory
from app.tools.orders import check_order_status, list_pending_orders
from app.tools.payments import initiate_momo_payment, get_failed_payments
from app.tools.analytics import get_revenue_summary, get_top_products, get_customer_history
from app.tools.notifications import get_business_hours, send_broadcast

claude = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

TOOL_REGISTRY = {
    "query_inventory": query_inventory,
    "check_order_status": check_order_status,
    "get_business_hours": get_business_hours,
    "get_revenue_summary": get_revenue_summary,
    "get_top_products": get_top_products,
    "list_pending_orders": list_pending_orders,
    "update_inventory": update_inventory,
    "get_failed_payments": get_failed_payments,
    "get_customer_history": get_customer_history,
    "send_broadcast": send_broadcast,
}

# Tools that receive the sender's phone number injected by the backend.
PHONE_INJECTED_TOOLS = {"initiate_momo_payment"}


async def execute_tools(content: list, sender: str) -> list:
    results = []
    for block in content:
        if block.type != "tool_use":
            continue
        tool_name = block.name
        tool_input = dict(block.input)

        try:
            if tool_name in PHONE_INJECTED_TOOLS:
                result = await initiate_momo_payment(customer_phone=sender, **tool_input)
            elif tool_name in TOOL_REGISTRY:
                result = await TOOL_REGISTRY[tool_name](**tool_input)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            result = {"error": str(e)}

        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": json.dumps(result, default=str),
        })
    return results


def extract_text(content: list) -> str:
    for block in content:
        if hasattr(block, "type") and block.type == "text":
            return block.text
    return ""


async def get_recent_messages(phone: str, limit: int = 12) -> list:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.phone == phone)
            .order_by(ConversationMessage.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
    return list(reversed(messages))


async def save_message(phone: str, role: str, content: str) -> None:
    async with AsyncSessionLocal() as db:
        msg = ConversationMessage(phone=phone, role=role, content=content)
        db.add(msg)
        await db.commit()


async def build_messages(phone: str, new_msg: str) -> list:
    from app.tools.orders import get_pending_order_for_phone

    recent = await get_recent_messages(phone, limit=12)
    pending_order = await get_pending_order_for_phone(phone)
    messages = []

    if pending_order:
        ctx = (
            f"ACTIVE PENDING ORDER:\n"
            f"  Order ID : {pending_order.id}\n"
            f"  Items    : {json.dumps(pending_order.items)}\n"
            f"  Total    : {pending_order.total_xaf} XAF\n"
            f"  MoMo ref : {pending_order.momo_ref}\n"
            f"  Status   : Awaiting payment confirmation"
        )
        messages += [
            {"role": "user", "content": f"[CONTEXT]\n{ctx}"},
            {"role": "assistant", "content": "Understood. I have the pending order context."},
        ]

    for msg in recent:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": new_msg})
    return messages


async def run_agent(sender: str, message: str) -> str:
    system = MERCHANT_SYSTEM if is_merchant(sender) else CUSTOMER_SYSTEM
    tools = get_tools(sender)
    messages = await build_messages(sender, message)

    for _ in range(10):
        response = await claude.messages.create(
            model=settings.CLAUDE_MODEL,
            system=system,
            tools=tools,
            messages=messages,
            max_tokens=1024,
        )

        if response.stop_reason == "end_turn":
            text = extract_text(response.content)
            return text or "Je suis désolé, je n'ai pas pu générer une réponse. Veuillez réessayer."

        if response.stop_reason == "tool_use":
            tool_results = await execute_tools(response.content, sender)
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

    return "Je suis désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer."
