from database.database import Base,engine,write_engine,read_engine,write_SessionLocal,read_SessionLocal,SessionLocal

def db_init():
    Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()

    try:
        yield db
    finally:
        db.close()

##replica architecture
def get_write_db():
    db=write_SessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_read_db():
    db=read_SessionLocal()

    try:
        yield db
    finally:
        db.close()