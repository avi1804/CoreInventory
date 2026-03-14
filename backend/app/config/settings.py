from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_HOST: str = "localhost"
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = ""
    DATABASE_NAME: str = "coreinventory"
    
    # SMTP Configuration - Set via environment variables
    # DO NOT hardcode credentials here - use .env file or env vars
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # Set via SMTP_USER environment variable
    SMTP_PASSWORD: str = ""  # Set via SMTP_PASSWORD environment variable
    SMTP_FROM_EMAIL: str = ""  # Set via SMTP_FROM_EMAIL env var
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}/{self.DATABASE_NAME}"
    
    class Config:
        env_file = ".env"


settings = Settings()
