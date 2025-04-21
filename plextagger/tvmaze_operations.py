import requests, re, logging, time
from sqlalchemy import insert
from sqlalchemy.orm import Session

from .models import FailedMatch, TMDBData, TVMazeData

base_url = "https://api.tvmaze.com/lookup/shows"

headers = {
    'accept': 'application/json',
}

_logger = logging.getLogger(__name__)

def _sanitize(s: str | None) -> str | None:
    if s is None:
        return None
    s = s.lower().replace(',', '_').replace(':', '_')
    return re.sub(r'\s+', '-', s)

def get_cached_show_details(plex_id: int, tvdb_id: str, session: Session) -> TVMazeData | None:
    cached_data = session.query(TVMazeData).filter_by(tvdb=tvdb_id).first()
    if cached_data:
        return cached_data
    cached_data = session.query(FailedMatch).filter_by(plex_id=plex_id, type='tvmaze').first()
    if cached_data:
        return None

    response = requests.get(base_url, headers=headers, params={ 'thetvdb': tvdb_id })
    backoff_seconds = 1
    while response.status_code == 429:
        _logger.warn(f'received 429 from tvmaze. waiting {backoff_seconds} seconds before retrying...\nheaders: {response.headers}, body: {response.text}')
        time.sleep(backoff_seconds)
        backoff_seconds *= 2

    if response.status_code == 404:
        _logger.warn(f'Failed to find tvmaze match for tvdb id {tvdb_id}')
        failure = FailedMatch(
            plex_id=plex_id,
            type='tvmaze',
            url = response.request.url)
        session.add(failure)
        session.commit()
        return None

    response.raise_for_status()
    result = response.json()

    def flatten(section_key, selector):
        section = result.get(section_key, None)
        if section is None:
            return ""
        return ','.join(sorted(set(j for j in (_sanitize(selector(i)) for i in section) if j is not None)))

    web_channel = result.get('webChannel')
    web_channel = web_channel['name'] if web_channel is not None else None

    network = result.get('network')
    network = network['name'] if network is not None else None

    data = TVMazeData(
        id=str(result['id']),
        tvdb=tvdb_id,
        type=_sanitize(result.get('type')),
        genres=flatten('genres', lambda x: x),
        network=_sanitize(network),
        web_channel=_sanitize(web_channel)
    )

    session.add(data)
    session.commit()

    return data

