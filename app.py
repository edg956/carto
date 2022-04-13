from config import Config, settings
from geoapp.db import init


def setup(settings: Config = settings):
    init(settings.db_config)
