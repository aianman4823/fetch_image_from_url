import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

osCurrentDirectory = os.getcwd()

user = os.environ["DB_USER"]
password = os.environ["DB_PASSWORD"]
host = os.environ["DB_HOST"]
database = os.environ["DATABASE"]


SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"


engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600, pool_pre_ping=True)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
Base = declarative_base()
