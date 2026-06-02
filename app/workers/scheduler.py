from app.config import settings
from app.services.whatsapp import whatsapp_client
from app.tools.analytics import get_revenue_summary, get_top_products
from app.tools.orders import get_pending_orders
from app.tools.inventory import get_low_stock_products


async def send_morning_brief(_ctx=None) -> None:
    """Daily morning brief sent to the merchant at 07:00 CAT."""
    summary = await get_revenue_summary("yesterday")
    top_prods = await get_top_products(limit=3, period="yesterday")
    pending = await get_pending_orders()
    low_stock = await get_low_stock_products()

    lines = [
        f"📊 *Rapport du jour — {settings.BUSINESS_NAME}*",
        "",
        f"💰 Recettes : {summary['total_xaf']:,} XAF",
        f"📦 Commandes : {summary['order_count']}",
        f"📈 Panier moyen : {summary['avg_order_xaf']:,} XAF",
    ]

    if top_prods:
        lines += ["", "🏆 Produits les plus vendus hier :"]
        for i, p in enumerate(top_prods, 1):
            lines.append(f"   {i}. {p['name']} — {p['qty']} vendus")

    if pending:
        lines.append(f"\n⏳ Commandes en attente : {len(pending)}")

    if low_stock:
        names = ", ".join(p["name"] for p in low_stock)
        lines.append(f"\n⚠️ Stock faible : {names}")

    await whatsapp_client.send_message(
        to=settings.MERCHANT_PHONE,
        body="\n".join(lines),
    )
