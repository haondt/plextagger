import requests, re, logging
from sqlalchemy.orm import Session

from .models import TMDBData
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

def get_cached_show_details(id: str, session: Session) -> TMDBData:
    return get_cached_details("show", id, session)

def get_cached_movie_details(id: str, session: Session) -> TMDBData:
    return get_cached_details("movie", id, session)

def get_cached_details(media_type: str, id: str, session: Session) -> TMDBData:
    cached_data = session.query(TMDBData).filter_by(id=id).first()
    if cached_data:
        return cached_data

    target_url = show_url if media_type == "show" else movie_url
    response = requests.get(target_url + f"/{id}", headers=headers, params={ 'language': 'en-US', 'append_to_response': 'keywords'})
    if (response.status_code == 429):
        _logger.error(f'received 429 from tmdb. headers: {response.headers}, body: {response.text}')
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

