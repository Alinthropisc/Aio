from pydantic import Field
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    token: str = Field(alias="BOT_TOKEN")
    webhook_url: str | None = Field(default=None, alias="BOT_WEBHOOK_URL")
    webhook_path: str = Field(default="/webhook", alias="BOT_WEBHOOK_PATH")
    use_webhook: bool = Field(default=False, alias="BOT_USE_WEBHOOK")
    drop_pending_updates: bool = Field(default=True, alias="BOT_DROP_PENDING_UPDATES")

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}
