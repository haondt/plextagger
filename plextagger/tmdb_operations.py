import requests, re, logging, time
from sqlalchemy.orm import Session

from .models import FailedMatch, TMDBData
from .configuration import configuration

base_url = "https://api.themoviedb.org/3"

movie_url = base_url + "/movie"
show_url = base_url + "/tv"

headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {configuration.tmdb_api_key}'
}

_logger = logging.getLogger(__name__)

def _sanitize(s: str) -> str:
    s = s.lower().replace(',', '_').replace(':', '_')
    return re.sub(r'\s+', '-', s)

def get_cached_show_details(plex_id: int, id: str, session: Session) -> TMDBData | None:
    return get_cached_details("show", plex_id, id, session)

def get_cached_movie_details(plex_id: int, id: str, session: Session) -> TMDBData | None:
    return get_cached_details("movie", plex_id, id, session)

def get_cached_details(media_type: str, plex_id: int,  id: str, session: Session) -> TMDBData | None:
    cached_data = session.query(TMDBData).filter_by(id=id).first()
    if cached_data:
        return cached_data
    cached_data = session.query(FailedMatch).filter_by(plex_id=plex_id, type='tvmaze').first()
    if cached_data:
        return None

    target_url = show_url if media_type == "show" else movie_url
    response = requests.get(target_url + f"/{id}", headers=headers, params={ 'language': 'en-US', 'append_to_response': 'keywords'})
    backoff_seconds = 1
    while response.status_code == 429:
        _logger.warn(f'received 429 from tmdb. waiting {backoff_seconds} seconds before retrying...\nheaders: {response.headers}, body: {response.text}')
        time.sleep(backoff_seconds)
        backoff_seconds *= 2

    if response.status_code == 404:
        _logger.warn(f'Failed to find tmdb match for tmdb id {id}')
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
        return ','.join(sorted(set(_sanitize(selector(i)) for i in section)))

    keywords = result.get("keywords", {})
    keywords = keywords.get("keywords", []) + keywords.get("results", [])
    keywords = ','.join(sorted(set(_sanitize(i['name']) for i in keywords)))

    data = TMDBData(
        id=id,
        keywords=keywords,
        genres=flatten('genres', lambda x: x['name']),
        production_companies=flatten('production_companies', lambda x: x['name']),
        production_countries=flatten('production_countries', lambda x: x['name']),
        created_by = flatten('created_by', lambda x: x['name']),
        networks = flatten('networks', lambda x: x['name'])
    )

    session.add(data)
    session.commit()

    return data

