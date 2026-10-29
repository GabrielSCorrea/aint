from os import path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

DATABASE_FILE = path.join(path.dirname(path.abspath(__file__)), "corrections.sqlite")
engine = create_engine(f"sqlite:///{DATABASE_FILE}", echo=False)

Base = declarative_base()
session = scoped_session(sessionmaker(bind=engine))

QUESTIONS = 4
MAX_GRADE = 5
