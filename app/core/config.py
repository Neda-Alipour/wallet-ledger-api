from pydantic_settings import BaseSettings, SettingsConfigDict

_base_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # This configures how the settings are loaded
    model_config = _base_config

class SecuritySetting(BaseSettings):

    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config = _base_config


# Create a single instance to be used across the app
db_settings = Settings()
security_settings = SecuritySetting()