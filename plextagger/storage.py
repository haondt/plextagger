from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from .models import Base
from .configuration import configuration

engine = create_engine(f'sqlite:///{configuration.db_path}/plex_data.db')
session_factory = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def create_session() -> Session:
    return session_factory()
