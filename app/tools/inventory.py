from sqlalchemy import select
from app.db.models import Product
from app.db.session import AsyncSessionLocal


async def query_inventory(product_name: str) -> dict:
    needle = product_name.lower()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Product).where(
                Product.name.ilike(f"%{product_name}%"),
                Product.is_active == True,
            )
        )
        by_name = result.scalars().all()

        # Also search products whose JSON alias list contains the needle
        all_result = await db.execute(
            select(Product).where(Product.is_active == True)
        )
        by_alias = [
            p for p in all_result.scalars().all()
            if p.name_aliases and any(needle in a.lower() for a in p.name_aliases)
            and p not in by_name
        ]
        products = list(by_name) + by_alias

    if not products:
        return {"found": False, "message": f"Aucun produit trouvé pour '{product_name}'"}

    return {
        "found": True,
        "products": [
            {
                "name": p.name,
                "price_xaf": p.price_xaf,
                "in_stock": p.stock_qty > 0,
                "qty": p.stock_qty,
            }
            for p in products
        ],
    }


async def update_inventory(product_name: str, new_qty: int) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Product).where(Product.name.ilike(f"%{product_name}%"), Product.is_active == True)
        )
        product = result.scalar_one_or_none()
        if not product:
            return {"success": False, "message": "Produit non trouvé"}
        old_qty = product.stock_qty
        product.stock_qty = new_qty
        await db.commit()

    return {"success": True, "product": product.name, "old_qty": old_qty, "new_qty": new_qty}


async def get_low_stock_products() -> list:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Product).where(
                Product.stock_qty <= Product.low_stock_threshold,
                Product.is_active == True,
            )
        )
        products = result.scalars().all()

    return [{"name": p.name, "qty": p.stock_qty, "threshold": p.low_stock_threshold} for p in products]
