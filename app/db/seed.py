from sqlalchemy import select, func
from app.db.models import Product
from app.db.session import AsyncSessionLocal

SAMPLE_PRODUCTS = [
    {
        "name": "Poulet braisé (entier)",
        "name_aliases": ["poulet", "chicken", "braisé", "nyama ya nkoko"],
        "price_xaf": 5000,
        "stock_qty": 20,
        "low_stock_threshold": 5,
    },
    {
        "name": "Poisson fumé (1 kg)",
        "name_aliases": ["poisson", "fish", "mbisi", "fumé"],
        "price_xaf": 3500,
        "stock_qty": 15,
        "low_stock_threshold": 3,
    },
    {
        "name": "Riz parfumé (5 kg)",
        "name_aliases": ["riz", "rice", "loso"],
        "price_xaf": 4500,
        "stock_qty": 30,
        "low_stock_threshold": 5,
    },
    {
        "name": "Huile de palme (1 L)",
        "name_aliases": ["huile", "oil", "mafuta", "palme"],
        "price_xaf": 1200,
        "stock_qty": 40,
        "low_stock_threshold": 10,
    },
    {
        "name": "Savon de ménage (x5)",
        "name_aliases": ["savon", "soap", "nsabuni"],
        "price_xaf": 1500,
        "stock_qty": 50,
        "low_stock_threshold": 10,
    },
    {
        "name": "Sucre en poudre (1 kg)",
        "name_aliases": ["sucre", "sugar", "sukari"],
        "price_xaf": 800,
        "stock_qty": 60,
        "low_stock_threshold": 10,
    },
    {
        "name": "Café soluble Nescafé (200 g)",
        "name_aliases": ["café", "coffee", "nescafe", "kafé"],
        "price_xaf": 2500,
        "stock_qty": 25,
        "low_stock_threshold": 5,
    },
    {
        "name": "Farine de manioc (2 kg)",
        "name_aliases": ["farine", "manioc", "cassava", "fufu", "kwanga"],
        "price_xaf": 1800,
        "stock_qty": 35,
        "low_stock_threshold": 5,
    },
]


async def seed_products() -> None:
    async with AsyncSessionLocal() as db:
        count = await db.scalar(select(func.count()).select_from(Product))
        if count and count > 0:
            return  # already seeded

        for p in SAMPLE_PRODUCTS:
            db.add(Product(**p))
        await db.commit()
        print(f"[SEED] Inserted {len(SAMPLE_PRODUCTS)} sample products.")
