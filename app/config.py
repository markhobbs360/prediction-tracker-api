from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/prediction_tracker"
    GOOGLE_CLIENT_ID: str = ""
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_EXPIRY_HOURS: int = 24
    JIRA_BASE_URL: str = "https://fundmetric.atlassian.net"
    JIRA_EMAIL: str = ""
    JIRA_API_TOKEN: str = ""
    CORS_ORIGINS: str = "http://localhost:5173"
    SHARED_PASSWORD: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
