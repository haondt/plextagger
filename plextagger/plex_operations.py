from plexapi.server import PlexServer
from .models import Media
from .configuration import configuration
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


# update the mirrored list of media in the db
def ingest_media(plex, session, run_id):
    for section in plex.library.sections():
        if section.type not in ['movie', 'show']:
            continue
        for item in section.search(limit=configuration.section_batch_size, filters={"genre!": "PT__processed"}):
            # for item in section.recentlyAdded():
            # for item in section.all():
            # item.reload()
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

def set_tags(plex: PlexServer, tags: list[str], ratingKey: int):
    plex_item = plex.fetchItem(ratingKey)
    if plex_item is None:
        raise Exception(f'Could not find item with rating key {ratingKey}')
    existing_genres = [str(i) for i in plex_item.genres]
    add_genres = [i for i in tags if i not in existing_genres]
    plex_item.addGenre(add_genres, locked=True)
    plex_item.reload()

def remove_pt_tags(plex: PlexServer, ratingKey: int):
    plex_item = plex.fetchItem(ratingKey)
    if plex_item is None:
        raise Exception(f'Could not find item with rating key {ratingKey}')
    existing_genres = [str(i) for i in plex_item.genres]
    remove_genres = [i for i in existing_genres if i.startswith('PT_')]
    plex_item.removeGenre(remove_genres, locked=True)
    plex_item.reload()


