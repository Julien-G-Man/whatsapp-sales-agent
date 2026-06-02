from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

# asyncpg does not accept these as query parameters
_STRIP_PARAMS = {"sslmode", "channel_binding"}


def _prepare_url(url: str) -> tuple[str, dict]:
    """Normalize DATABASE_URL for asyncpg and return extra connect_args.

    Neon injects: postgresql://...?sslmode=require&channel_binding=require
    asyncpg needs: postgresql+asyncpg://...  +  connect_args={"ssl": True}
    """
    connect_args: dict = {}
    needs_ssl = "sslmode=require" in url

    # Convert dialect prefix
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Strip params asyncpg rejects, preserving any others
    parsed = urlparse(url)
    params = {k: v for k, v in parse_qs(parsed.query, keep_blank_values=True).items()
              if k not in _STRIP_PARAMS}
    url = urlunparse(parsed._replace(query=urlencode(params, doseq=True)))

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
