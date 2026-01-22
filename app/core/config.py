from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # This configures how the settings are loaded
    model_config = SettingsConfigDict(env_file=".env")

# Create a single instance to be used across the app
settings = Settings()