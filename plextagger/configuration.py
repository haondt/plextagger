import os
import logging
def parse_bool_env_var(var_name, default=False):
    """Convert an environment variable to a boolean value.
    
    Returns True if value is 'true', '1', or any non-zero number (case-insensitive).
    Returns False for 'false', '0', None, or any other value.
    
    Args:
        var_name (str): Name of the environment variable to parse
        default (bool): Default value if variable is not set (default: False)
    
    Returns:
        bool: Parsed boolean value
    """
    value = os.getenv(var_name)
    if value is not None:
        value_str = str(value).lower()
        return value_str in ('true', '1') or \
               (value_str.isdigit() and int(value_str) != 0)
    return default

class Config:
    def __init__(self):
        self.plex_url = os.environ['PLEX_URL'].rstrip('/')
        self.plex_token = os.environ['PLEX_TOKEN']
        self.log_level = {
            'CRITICAL': logging.CRITICAL,
            'FATAL': logging.FATAL,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'WARN': logging.WARN,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'NOTSET': logging.NOTSET,
        }[os.getenv('LOG_LEVEL', 'INFO').upper()]

        self.log_template = os.getenv('LOG_TEMPLATE', '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')
        self.db_path = os.path.abspath(os.getenv('DB_PATH', '.')).rstrip('/')


configuration = Config()

