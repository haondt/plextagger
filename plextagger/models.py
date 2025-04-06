from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import UUID
engine = create_engine('sqlite:///plextagger.db')
Base = declarative_base()

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tmdb = Column(String)
    tvdb = Column(String)
    imdb = Column(String)
    tags = Column(String)
    created_at = Column(DateTime)
    run_id = Column(UUID)

