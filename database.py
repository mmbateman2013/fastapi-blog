"""Helper file for DB communication"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Class for DB Base"""


def get_db():
    """Method to get the DB"""
    with SESSION_LOCAL() as db:
        yield db
