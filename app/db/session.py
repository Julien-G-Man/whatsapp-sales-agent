import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings


def _prepare_url(url: str) -> tuple[str, dict]:
    """Normalize DATABASE_URL for asyncpg and return extra connect_args.

    Render/Neon inject  postgresql://...?sslmode=require
    asyncpg needs:      postgresql+asyncpg://...  + connect_args={"ssl": True}
    """
    connect_args: dict = {}
    needs_ssl = "sslmode=require" in url

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Strip sslmode — asyncpg rejects it as an unknown query parameter
    url = re.sub(r"[?&]sslmode=\w+", "", url).rstrip("?")

    if needs_ssl:
        connect_args["ssl"] = True

    return url, connect_args


_db_url, _ssl_args = _prepare_url(settings.DATABASE_URL)
_is_sqlite = _db_url.startswith("sqlite")
_engine_kwargs: dict = {"echo": False}
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_pre_ping"] = True
    if _ssl_args:
        _engine_kwargs["connect_args"] = _ssl_args

engine = create_async_engine(_db_url, **_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
