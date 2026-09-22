from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    WRITE_DB_URL:str
    READ_DB_URL:str
    REDIS_URL:str
    SECRET_KEY:str
    ALGORITHM:str

    class Config:
        env_file=".env"

settings=Settings()