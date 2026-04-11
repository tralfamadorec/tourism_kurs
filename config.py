from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf_8"

settings = Settings()