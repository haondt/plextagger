from .models import Media
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

# update the mirrored list of media in the db
def ingest_media(plex, session, run_id):
    for section in plex.library.sections():
        if section.type not in ['movie', 'show']:
            continue
        for item in section.recentlyAdded():
            # for item in section.all(): # TODO: switch back to this
            try:
                guids = {g.id.split('://')[0]: g.id.split('://')[1] for g in item.guids}
                tags = ','.join(sorted([i.tag for i in item.genres]))
                media = Media(
                    id=item.ratingKey,
                    name=item.title,
                    type=item.type,
                    tmdb=guids.get('tmdb'),
                    tvdb=guids.get('tvdb'),
                    imdb=guids.get('imdb'),
                    tags=tags,
                    created_at=datetime.now(),
                    run_id=run_id
                )
                session.merge(media)
            except Exception as e:
                _logger.error(f"Error processing item {item.title}: {e}")

# remove any media in the db that was added from a different run
def clean_old_runs(session, run_id):
    try:
        session.query(Media).filter(Media.run_id != run_id).delete()
    except Exception as e:
        _logger.error(f"Error cleaning old runs: {e}")
