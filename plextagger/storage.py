from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .configuration import configuration

engine = create_engine(f'sqlite:///{configuration.db_path}/plex_data.db')
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    return Session()
