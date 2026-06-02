from arq import cron
from app.workers.scheduler import send_morning_brief


class WorkerSettings:
    """ARQ worker configuration."""
    functions = []
    cron_jobs = [
        cron(send_morning_brief, hour=6, minute=0),  # 07:00 CAT = 06:00 UTC
    ]
    redis_settings = None  # Set from app.config at startup

    @classmethod
    def configure(cls, redis_url: str):
        from arq.connections import RedisSettings
        cls.redis_settings = RedisSettings.from_dsn(redis_url)
