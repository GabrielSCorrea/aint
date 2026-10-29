from os import path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

DATABASE_FILE = path.join(path.dirname(path.abspath(__file__)), "resolutions.sqlite")
engine = create_engine(f"sqlite:///{DATABASE_FILE}", echo=False)

Base = declarative_base()
session = scoped_session(sessionmaker(bind=engine))

INVALID_DATA_FAULT = 1
ALREADY_PRINTED_FAULT = 2
