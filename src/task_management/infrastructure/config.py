from __future__ import annotations

import os


class Settings:
    def __init__(self) -> None:
        self.app_env = os.getenv("APP_ENV", "dev")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")


settings = Settings()
