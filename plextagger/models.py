from sqlalchemy import Boolean, create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import UUID
engine = create_engine('sqlite:///plextagger.db')
Base = declarative_base()

# represents a single media item, i.e. a movie or tv show
class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tmdb: Mapped[str] = mapped_column(index=True)
    tvdb = Column(String, index=True)
    imdb = Column(String, index=True)
    tags = Column(String)
    type: Mapped[str] = mapped_column()
    created_at = Column(DateTime)
    run_id = Column(UUID)
    initialized: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

class TMDBData(Base):
    __tablename__ = 'tmdb_media'
    id = Column(String, primary_key=True)
    keywords = Column(String)
    genres = Column(String)
    production_companies = Column(String)
    created_by = Column(String)
    networks = Column(String)
    production_countries = Column(String)

class TVMazeData(Base):
    __tablename__ = 'tvmaze_media'
    id: Mapped[str] = mapped_column(primary_key=True)
    tvdb: Mapped[str] = mapped_column(unique=True, index=True)
    type: Mapped[str | None] = mapped_column()
    genres: Mapped[str] = mapped_column()
    network: Mapped[str | None] = mapped_column()
    web_channel: Mapped[str | None] = mapped_column()
