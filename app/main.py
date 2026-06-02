from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.migrations import init_db
from app.db.seed import seed_products
from app.api.health import router as health_router
from app.api.webhook import router as webhook_router
from app.api.momo_webhook import router as momo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_products()
    yield


app = FastAPI(
    title="WhatsApp Sales Agent",
    description="Agentic commerce for Congo-Brazzaville — powered by Claude & MTN MoMo",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router, tags=["system"])
app.include_router(webhook_router, tags=["whatsapp"])
app.include_router(momo_router, tags=["momo"])
