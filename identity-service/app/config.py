from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    ALLOWED_HOSTS: str = "localhost"
    CORS_ORIGINS: str = "*"

    JWT_SECRET_KEY: str = "supersecret" 
    JWT_ALGORITHM: str = "HS256"         
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7    

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
