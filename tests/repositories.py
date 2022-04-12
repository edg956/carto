import pytest

from geoapp import repositories


@pytest.fixture
def inmemory_repository():
    repo = repositories.InMemoryRepository()
    yield repo
    repo._db.clear()


class TestInMemoryRepository:
    def test_user_exists_returns_true(self, inmemory_repository):
        assert inmemory_repository.create_user("username", "password") is True
        assert inmemory_repository.check_user_credentials("username", "password") is True

    def test_user_exists_with_nonexistent_user_returns_false(self, inmemory_repository):
        print(inmemory_repository._db)
        assert inmemory_repository.check_user_credentials("username", "password") is False
