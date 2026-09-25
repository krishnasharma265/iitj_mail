from sqlalchemy.orm import sessionmaker
from common.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base=declarative_base()

##single DB archetecture
db_url=settings.DATABASE_URL

engine=create_engine(db_url)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

##replica architecture
write_db_url=settings.WRITE_DB_URL
read_db_url=settings.READ_DB_URL

write_engine=create_engine(write_db_url)
read_engine=create_engine(read_db_url)

write_SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=write_engine)
read_SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=read_engine)
