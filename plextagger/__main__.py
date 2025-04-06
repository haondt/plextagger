import plexapi.server
import uuid

from .plex_operations import clean_old_runs, update_media
from .storage import get_session, init_db, engine
from .configuration import configuration
import logging
import datetime

logging.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))
logging.basicConfig(format=configuration.log_template, level=configuration.log_level)

_logger = logging.getLogger(__name__)

plex = plexapi.server.PlexServer(configuration.plex_url, configuration.plex_token)

if __name__ == "__main__":
    init_db()
    session = get_session()
    try:
        current_run_id = uuid.uuid4()
        update_media(plex, session, current_run_id)
        clean_old_runs(session, current_run_id)
        session.commit()
    except Exception as e:
        _logger.error(f"Error in main process: {e}")
        session.rollback()
    finally:
        session.close()
