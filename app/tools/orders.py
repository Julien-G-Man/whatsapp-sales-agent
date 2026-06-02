from sqlalchemy import select
from app.db.models import Order
from app.db.session import AsyncSessionLocal


async def check_order_status(order_id: int) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()

    if not order:
        return {"found": False, "message": "Commande non trouvée"}

    return {
        "found": True,
        "order_id": order.id,
        "status": order.status,
        "total_xaf": order.total_xaf,
        "items": order.items,
    }


async def get_pending_orders() -> list:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order).where(Order.status == "pending"))
        orders = result.scalars().all()

    return [
        {
            "order_id": o.id,
            "customer_phone": o.customer_phone,
            "total_xaf": o.total_xaf,
            "items": o.items,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]


async def list_pending_orders() -> dict:
    orders = await get_pending_orders()
    return {"count": len(orders), "orders": orders}


async def get_pending_order_for_phone(phone: str) -> Order | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order)
            .where(Order.customer_phone == phone, Order.status == "pending")
            .order_by(Order.created_at.desc())
        )
        return result.scalar_one_or_none()


async def get_order_by_momo_ref(momo_ref: str) -> Order | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order).where(Order.momo_ref == momo_ref))
        return result.scalar_one_or_none()


async def update_order_status(order_id: int, status: str) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            order.status = status
            await db.commit()
