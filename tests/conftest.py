import pytest

from app import setup
from config import settings
from geoapp.db import database as db
from geoapp.services import TDatabase


@pytest.fixture(scope="session")
def database() -> TDatabase:
    try:
        settings.test = True
        setup(settings)

        yield db

    finally:
        db.teardown()
