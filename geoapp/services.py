import abc
from datetime import date
import typing as T

from geoapp import db


TDatabase = T.Type[db.Database]


class AbstractQueryService(abc.ABC):
    @abc.abstractmethod
    def get_map(self, start_date: date, end_date: date) -> dict:
        pass

    @abc.abstractmethod
    def get_turnover(self, start_date: date, end_date: date, by: T.Iterable[str]) -> dict:
        pass

    @abc.abstractmethod
    def get_turnover_by_age_and_gender(self, start_date: date, end_date: date) -> dict:
        pass

    @abc.abstractmethod
    def get_turnover_by_time_and_gender(self, start_date: date, end_date: date) -> dict:
        pass


class DummyQueryService(AbstractQueryService):
    def __init__(self, data: dict):
        self._data = data

    def get_map(self, start_date: date, end_date: date) -> dict:
        return self._data['map']

    def get_turnover(self, start_date: date, end_date: date) -> dict:
        return self._data['turnover']

    def get_turnover_by_age_and_gender(self, start_date: date, end_date: date) -> dict:
        return self._data['turnover_by_age_and_gender']

    def get_turnover_by_time_and_gender(self, start_date: date, end_date: date) -> dict:
        return self._data['turnover_by_time_gender']


class PostgresQueryService(AbstractQueryService):
    class DatabaseNotInitialized(Exception):
        pass

    def __init__(self, database: TDatabase = None):
        if database is None:
            database = db.database

        self.db = database

    def get_map(self, start_date: date, end_date: date) -> dict:
        return self.db.execute_query("SELECT 1")

    def get_turnover(self, start_date: date, end_date: date) -> dict:
        return self.db.execute_query("SELECT 1")

    def get_turnover_by_age_and_gender(self, start_date: date, end_date: date) -> dict:
        return self.db.execute_query("SELECT 1")

    def get_turnover_by_time_and_gender(self, start_date: date, end_date: date) -> dict:
        return self.db.execute_query("SELECT 1")
