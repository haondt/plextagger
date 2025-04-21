import plexapi.server
import uuid

from .models import Media, TMDBData, TVMazeData

from .plex_operations import clean_old_runs, ingest_media, remove_pt_tags, set_tags
from .storage import create_session, init_db, engine
from .configuration import configuration
from .tmdb_operations import get_cached_movie_details, get_cached_show_details
from . import tvmaze_operations as tvmaze
import logging
import datetime

logging.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))
logging.basicConfig(format=configuration.log_template, level=configuration.log_level)

_logger = logging.getLogger(__name__)

_logger.info(f'Attempting to establish connection to plex server {configuration.plex_url}')
plex = plexapi.server.PlexServer(configuration.plex_url, configuration.plex_token)

def update_plex_cache():
    session = create_session()
    try:
        current_run_id = uuid.uuid4()
        ingest_media(plex, session, current_run_id)
        clean_old_runs(session, current_run_id)
        session.commit()
    finally:
        session.close()


def process_cached_media():
    session = create_session()
    batch_size = 100
    offset = 0
    try:
        total = session.query(Media).count()
        _logger.info(f'Found {total} media items.')
        while True:
            batch = session.query(Media) \
                .limit(batch_size) \
                .offset(offset) \
                .all()

            if not batch:
                break
            
            for i, item in enumerate(batch):
                _logger.info(f'Processing item \'{item.name}\' ({i + offset + 1}/{total})')

                tmdb_details: TMDBData | None = None
                tvmaze_details: TVMazeData | None = None
                if item.tmdb is not None:
                    if item.type == "show":
                        tmdb_details = get_cached_show_details(item.id, item.tmdb, session)
                    elif item.type == "movie":
                        tmdb_details = get_cached_movie_details(item.id, item.tmdb, session)
                if item.tvdb is not None:
                    if item.type == "show":
                        tvmaze_details = tvmaze.get_cached_show_details(item.id, item.tvdb, session)

                original_tags: list[str] = item.tags.split(',') if len(item.tags) > 0 else []
                new_tags: list[str] = [i for i in original_tags]
                new_tags.append('PT__processed')
                prefix = 'PT_'
                if tmdb_details is not None:
                    if len(tmdb_details.keywords) > 0:
                        new_tags += [f'{prefix}{i}' for i in tmdb_details.keywords.split(',')]
                    if len(tmdb_details.genres) > 0:
                        new_tags += [f'{prefix}{i}' for i in tmdb_details.genres.split(',')]
                    if len(tmdb_details.production_companies) > 0:
                        new_tags += [f'{prefix}producer:{i}' for i in tmdb_details.production_companies.split(',')]
                    if len(tmdb_details.networks) > 0:
                        new_tags += [f'{prefix}provider:{i}' for i in tmdb_details.networks.split(',')]
                    if len(tmdb_details.production_countries) > 0:
                        new_tags += [f'{prefix}country:{i}' for i in tmdb_details.production_countries.split(',')]
                if tvmaze_details is not None:
                    if tvmaze_details.type is not None:
                        new_tags.append(f'{prefix}{tvmaze_details.type}')
                    if len(tvmaze_details.genres) > 0:
                        new_tags += [f'{prefix}{i}' for i in tvmaze_details.genres.split(',')]
                    if tvmaze_details.network is not None and len(tvmaze_details.network) > 0:
                        new_tags.append(f'{prefix}provider:{tvmaze_details.network}')
                    if tvmaze_details.web_channel is not None and len(tvmaze_details.web_channel) > 0:
                        new_tags.append(f'{prefix}provider:{tvmaze_details.web_channel}')
                new_tags = sorted(set(i for i in new_tags if i is not None and len(i) > 0))

                if new_tags != original_tags:
                    _logger.info(f'Updating tags for item \'{item.name}\': {new_tags}')
                    set_tags(plex, new_tags, item.id)
                session.delete(item)
            
            session.commit()

            offset += batch_size
    except Exception as e:
        _logger.error(f"Error in main process: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()

    _logger.info(f"Starting plex cache update.")
    update_plex_cache()
    _logger.info(f"Plex cache update complete.")

    _logger.info(f"processing queue")
    process_cached_media()
    _logger.info(f"queue processing complete.")
