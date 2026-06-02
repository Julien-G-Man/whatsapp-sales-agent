from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "business": settings.BUSINESS_NAME,
        "city": settings.BUSINESS_CITY,
        "env": settings.ENV,
    }
