import plexapi.server
import uuid

from .models import Media

from .plex_operations import clean_old_runs, ingest_media
from .storage import create_session, init_db, engine
from .configuration import configuration
from .tmdb_operations import get_cached_movie_details, get_cached_show_details
import logging
import datetime

logging.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))
logging.basicConfig(format=configuration.log_template, level=configuration.log_level)

_logger = logging.getLogger(__name__)

plex = plexapi.server.PlexServer(configuration.plex_url, configuration.plex_token)

def update_plex_cache():
    session = create_session()
    try:
        current_run_id = uuid.uuid4()
        ingest_media(plex, session, current_run_id)
        clean_old_runs(session, current_run_id)
        session.commit()
    except Exception as e:
        _logger.error(f"Error in main process: {e}")
        session.rollback()
    finally:
        session.close()


def initialize_media():
    session = create_session()
    batch_size = 100
    offset = 0
    try:
        while True:
            batch = session.query(Media).filter_by(initialized=False) \
                .limit(batch_size) \
                .offset(offset) \
                .all()
            if not batch:
                break
            # for item in batch:
            #     item.initialized = True
            break
        session.commit()
    except Exception as e:
        _logger.error(f"Error in main process: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()

    # _logger.info(f"Starting plex cache update.")
    # update_plex_cache()
    # _logger.info(f"Plex cache update complete.")


    session = create_session()
    batch_size = 100
    offset = 0
    try:
        batch = session.query(Media).filter_by(initialized=False) \
            .limit(batch_size) \
            .offset(offset) \
            .all()

        for item in batch:
            if item.tmdb is None:
                continue

            if item.type == "show":
                details = get_cached_show_details(item.tmdb, session)
            elif item.type == "movie":
                details = get_cached_movie_details(item.tmdb, session)

        session.commit()
    except Exception as e:
        _logger.error(f"Error in main process: {e}")
        session.rollback()
    finally:
        session.close()




