from .models import Media
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

def update_media(plex, session, run_id):
    for section in plex.library.sections():
        for item in section.recentlyAdded():
        # for item in section.all():
            try:
                guids = {g.id.split('://')[0]: g.id.split('://')[1] for g in item.guids}
                tags = ','.join([i.tag for i in item.genres])
                media = Media(
                    id=item.ratingKey,
                    name=item.title,
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

def clean_old_runs(session, run_id):
    try:
        session.query(Media).filter(Media.run_id != run_id).delete()
    except Exception as e:
        _logger.error(f"Error cleaning old runs: {e}")
