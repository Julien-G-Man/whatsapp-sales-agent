from datetime import datetime, timedelta
from sqlalchemy import select, func
from app.db.models import Transaction, Order, Product
from app.db.session import AsyncSessionLocal


async def get_revenue_summary(period: str = "today") -> dict:
    now = datetime.utcnow()
    start = {
        "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
        "yesterday": (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
        "week": now - timedelta(days=7),
        "month": now - timedelta(days=30),
    }.get(period, now.replace(hour=0, minute=0, second=0, microsecond=0))

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(
                func.sum(Transaction.amount_xaf).label("total"),
                func.count(Transaction.id).label("count"),
            ).where(
                Transaction.status == "confirmed",
                Transaction.confirmed_at >= start,
            )
        )
        row = result.one()

    total = row.total or 0
    count = row.count or 0
    return {
        "period": period,
        "total_xaf": total,
        "order_count": count,
        "avg_order_xaf": (total // count) if count else 0,
    }


async def get_top_products(limit: int = 3, period: str = "today") -> list:
    now = datetime.utcnow()
    start = {
        "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
        "yesterday": (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
        "week": now - timedelta(days=7),
        "month": now - timedelta(days=30),
    }.get(period, now.replace(hour=0, minute=0, second=0, microsecond=0))

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order)
            .where(Order.status == "paid", Order.created_at >= start)
        )
        orders = result.scalars().all()

    product_counts: dict[str, int] = {}
    for order in orders:
        if order.items:
            for item in order.items:
                name = item.get("name", str(item.get("product_id", "unknown")))
                product_counts[name] = product_counts.get(name, 0) + item.get("qty", 1)

    sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"name": name, "qty": qty} for name, qty in sorted_products[:limit]]


async def get_customer_history(customer_phone: str) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order)
            .where(Order.customer_phone == customer_phone)
            .order_by(Order.created_at.desc())
            .limit(10)
        )
        orders = result.scalars().all()

    return {
        "customer_phone": customer_phone,
        "total_orders": len(orders),
        "orders": [
            {
                "order_id": o.id,
                "status": o.status,
                "total_xaf": o.total_xaf,
                "items": o.items,
                "date": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ],
    }
