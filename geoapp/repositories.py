import abc
import hashlib

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def create_user(self, username: str, password: str) -> bool:
        pass

    @abc.abstractmethod
    def check_user_credentials(self, username: str, password: str) -> bool:
        pass


class InMemoryRepository(AbstractRepository):
    _hasher = hashlib.sha256()                                  # TODO: should use pbkdf2
    _db = {}

    def create_user(self, username: str, password: str) -> bool:
        self._hasher.update(password)
        self._db[username] = self._hasher.hexdigest()
        return True

    def check_user_credentials(self, username: str, password: str) -> bool:
        self._hasher.update(password)
        return username in self._db and self._db[username] == self._hasher.hexdigest()
