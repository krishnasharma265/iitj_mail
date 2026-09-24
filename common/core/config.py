import os 
from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings

load_dotenv()
# env_path = Path(__file__).resolve().parent.parent.parent / ".env"
class Settings(BaseSettings):
    DATABASE_URL: str
    WRITE_DB_URL:str
    READ_DB_URL:str
    REDIS_URL:str
    SECRET_KEY:str
    ALGORITHM:str

    class config:
        env_file=".env"
settings=Settings()