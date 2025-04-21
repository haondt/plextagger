from sqlalchemy import Boolean, ForeignKey, UniqueConstraint, create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UUID
engine = create_engine('sqlite:///plextagger.db')
Base = declarative_base()

# represents a single media item, i.e. a movie or tv show
class Media(Base):
    __tablename__ = 'media'
    id: Mapped[int] = mapped_column(primary_key=True)
    name = Column(String)
    tmdb: Mapped[str | None] = mapped_column(index=True)
    tvdb: Mapped[str | None] = mapped_column(index=True)
    imdb: Mapped[str | None] = mapped_column(index=True)
    tags: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    created_at = Column(DateTime)
    run_id = Column(UUID)

class TMDBData(Base):
    __tablename__ = 'tmdb_media'
    id = Column(String, primary_key=True)
    keywords: Mapped[str] = mapped_column()
    genres: Mapped[str] = mapped_column()
    production_companies: Mapped[str] = mapped_column()
    created_by = Column(String)
    networks: Mapped[str] = mapped_column()
    production_countries: Mapped[str] = mapped_column()

class TVMazeData(Base):
    __tablename__ = 'tvmaze_media'
    id: Mapped[str] = mapped_column(primary_key=True)
    tvdb: Mapped[str] = mapped_column(unique=True, index=True)
    type: Mapped[str | None] = mapped_column()
    genres: Mapped[str] = mapped_column()
    network: Mapped[str | None] = mapped_column()
    web_channel: Mapped[str | None] = mapped_column()

class FailedMatch(Base):
    __tablename__ = 'failed_matches'
    id: Mapped[int] = mapped_column(primary_key=True)
    plex_id: Mapped[int] = mapped_column(index=True)
    type: Mapped[str] = mapped_column(index=True)
    url: Mapped[str] = mapped_column()
    __table_args__ = (
        UniqueConstraint('plex_id', 'type', name='_plex_id_type_uc'),
    )

    media: Mapped[Media] = relationship(passive_deletes=False)

