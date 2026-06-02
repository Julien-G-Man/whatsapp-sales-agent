from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"

    WHATSAPP_API_KEY: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""

    MOMO_SUBSCRIPTION_KEY: str = ""
    MOMO_API_USER: str = ""
    MOMO_API_KEY: str = ""
    MOMO_ENVIRONMENT: str = "sandbox"
    MOMO_CALLBACK_URL: str = ""

    DATABASE_URL: str = "sqlite+aiosqlite:///./momoagent.db"
    REDIS_URL: str = ""

    MERCHANT_PHONE: str = ""
    BUSINESS_NAME: str = ""
    BUSINESS_CITY: str = ""

    ENV: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
