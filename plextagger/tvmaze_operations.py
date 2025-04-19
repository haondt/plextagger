import requests, re, logging
from sqlalchemy.orm import Session

from .models import TMDBData, TVMazeData

base_url = "https://api.tvmaze.com/lookup/shows"

headers = {
    'accept': 'application/json',
}

_logger = logging.getLogger(__name__)

def _sanitize(s: str) -> str:
    s = s.lower().replace(',', '_').replace(':', '_')
    return re.sub(r'\s+', '-', s)

def get_cached_show_details(tvdb_id: str, session: Session) -> TVMazeData:
    cached_data = session.query(TVMazeData).filter_by(tvdb=tvdb_id).first()
    if cached_data:
        return cached_data

    response = requests.get(base_url, headers=headers, params={ 'thetvdb': tvdb_id })
    if (response.status_code == 429):
        _logger.error(f'received 429 from tvmaze. headers: {response.headers}, body: {response.text}')
    response.raise_for_status()
    result = response.json()

    def flatten(section_key, selector):
        section = result.get(section_key, None)
        if section is None:
            return ""
        return ','.join(sorted(set(_sanitize(selector(i)) for i in section)))

    web_channel = result.get('webChannel')
    web_channel = web_channel['name'] if web_channel is not None else None

    network = result.get('network')
    network = network['name'] if network is not None else None

    data = TVMazeData(
        id=str(result['id']),
        tvdb=tvdb_id,
        type=_sanitize(result.get('type', '')),
        genres=flatten('genres', lambda x: x),
        network=network,
        web_channel=web_channel
    )

    session.add(data)
    session.commit()

    return data

