import pytest

from app import setup
from config import settings
from geoapp.db import database as db


@pytest.fixture(scope="session")
def database():
    try:
        settings.db_config.database = "test_database"
        setup(settings)

        yield

    finally:
        db.teardown()
