import pytest

from geoapp import repositories


@pytest.fixture()
def inmemory_repository():
    repo = repositories.InMemoryRepository()
    yield repo
    repo._db = {}


class InMemoryRepositoryTestClass:
    def test_user_exists_returns_true(self, repo):
        assert repo.create_user("username", "password") is True
        assert repo.check_user_credentials("username", "password") is True

    def test_user_exists_with_nonexistent_user_returns_false(self, repo):
        assert repo.check_user_credentials("username", "password") is False
