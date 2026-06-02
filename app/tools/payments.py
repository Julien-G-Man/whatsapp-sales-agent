import uuid
from datetime import datetime
from sqlalchemy import select
from app.db.models import Order, Transaction, Product
from app.db.session import AsyncSessionLocal
from app.services.momo import momo_client


async def initiate_momo_payment(customer_phone: str, items: list, total_xaf: int) -> dict:
    async with AsyncSessionLocal() as db:
        order = Order(
            customer_phone=customer_phone,
            items=items,
            total_xaf=total_xaf,
            status="pending",
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)

        momo_ref = str(uuid.uuid4())
        await momo_client.request_to_pay(
            amount=total_xaf,
            currency="XAF",
            external_id=momo_ref,
            payer_phone=customer_phone,
            payer_message=f"Paiement commande #{order.id}",
        )

        order.momo_ref = momo_ref
        txn = Transaction(
            order_id=order.id,
            momo_ref=momo_ref,
            amount_xaf=total_xaf,
            customer_phone=customer_phone,
            status="initiated",
        )
        db.add(txn)
        await db.commit()

        return {
            "order_id": order.id,
            "momo_ref": momo_ref,
            "instruction": "Ask customer to approve the MoMo push request on their phone",
        }


async def get_failed_payments(limit: int = 10) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Transaction)
            .where(Transaction.status == "failed")
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        txns = result.scalars().all()

    return {
        "count": len(txns),
        "transactions": [
            {
                "momo_ref": t.momo_ref,
                "amount_xaf": t.amount_xaf,
                "customer_phone": t.customer_phone,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in txns
        ],
    }


async def confirm_payment(momo_ref: str) -> None:
    async with AsyncSessionLocal() as db:
        txn_result = await db.execute(
            select(Transaction).where(Transaction.momo_ref == momo_ref)
        )
        txn = txn_result.scalar_one_or_none()
        if txn:
            txn.status = "confirmed"
            txn.confirmed_at = datetime.utcnow()
            await db.commit()


async def fail_payment(momo_ref: str) -> None:
    async with AsyncSessionLocal() as db:
        txn_result = await db.execute(
            select(Transaction).where(Transaction.momo_ref == momo_ref)
        )
        txn = txn_result.scalar_one_or_none()
        if txn:
            txn.status = "failed"
            await db.commit()


async def decrement_inventory(items: list) -> None:
    async with AsyncSessionLocal() as db:
        for item in items:
            result = await db.execute(
                select(Product).where(Product.id == item.get("product_id"))
            )
            product = result.scalar_one_or_none()
            if product:
                product.stock_qty = max(0, product.stock_qty - item.get("qty", 1))
        await db.commit()
