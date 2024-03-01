from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# SQLALCHEMY_DATABASE_URL_PROD = 'postgresql://postgres:123qwe123qwe@35.238.209.92/postgres'
# #SQLALCHEMY_DATABASE_URL_DEV = 'postgresql://postgres:123qwe123qwe@localhost/forgecode'

# if "DATABASE_URL" in os.environ:
#     SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]
# else:
#     SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:123qwe123qwe@localhost/forgecode'

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

print(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()