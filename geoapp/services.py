import abc
from datetime import date, timedelta
import typing as T

from dateutil.relativedelta import relativedelta

from geoapp import db
from geoapp.models import Age, Gender


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
        res = self.db.execute_query(
            "WITH aggregate AS ("
            "SELECT pc.code, ps.p_age, ps.p_gender, SUM(ps.amount) AS sum_amount "
            "FROM PostalCodes pc JOIN Payments ps "
            "ON pc.id = ps.postal_code_id "
            "WHERE ps.p_month >= %s AND ps.p_month <= %s "
            "GROUP BY pc.code, ps.p_age, ps.p_gender)\n"
            "SELECT pc.code, the_geom AS geometry, p_age, p_gender, sum_amount "
            "FROM PostalCodes pc JOIN aggregate a "
            "ON pc.code = a.code;",
            (start_date, end_date)
        )

        data = {}
        for code, geometry, age, gender, sum_ in res:
            if code not in data:
                data[code] = _get_base_dictionary()

            data[code]["geometry"] = geometry
            data[code]["aggregate"][age][gender] += sum_

        return {
            "results": [
                {
                    "geometry": data[code]["geometry"],
                    "turnover": data[code]["aggregate"]
                }
                for code in data
            ]
        }

    def get_turnover(self, start_date: date, end_date: date) -> dict:
        res = self.db.execute_query(
            "SELECT SUM(amount) FROM Payments WHERE p_month >= %s AND p_month <= %s",
            (start_date, end_date)
        )

        return {
            "results": res[0][0]
        }

    def get_turnover_by_age_and_gender(self, start_date: date, end_date: date) -> dict:
        res = self.db.execute_query(
            "SELECT p_age, p_gender, SUM(amount) "
            "FROM Payments "
            "WHERE p_month >= %s AND p_month <= %s "
            "GROUP BY p_age, p_gender",
            (start_date, end_date)
        )

        data = _get_aggregate_by_age_and_gender_dictionary()

        for age, gender, amount in res:
            data[age][gender] += amount

        return {
            "results": data
        }

    def get_turnover_by_time_and_gender(self, start_date: date, end_date: date) -> dict:
        res = self.db.execute_query(
            "SELECT TO_CHAR(p_month, 'yyyy-mm'), p_gender, SUM(amount) "
            "FROM Payments "
            "WHERE p_month >= %s AND p_month <= %s "
            "GROUP BY TO_CHAR(p_month, 'yyyy-mm'), p_gender",
            (start_date, end_date)
        )

        data = _get_aggregate_by_time_and_gender_dictionary(start_date, end_date)

        for tm, gender, amount in res:
            data[tm][gender] += amount

        return {
            "results": data
        }


def _get_base_dictionary() -> dict:
    base = {"geometry": None, "aggregate": {}}
    for age in Age:
        base["aggregate"][age] = {}
        for gender in Gender:
            base["aggregate"][age][gender] = 0
    return base


def _get_aggregate_by_age_and_gender_dictionary() -> dict:
    base = {}
    for age in Age:
        base[age] = {}
        for gender in Gender:
            base[age][gender] = 0
    return base


def _get_aggregate_by_time_and_gender_dictionary(start_date: date, end_date: date) -> dict:
    base = {}
    delta = relativedelta(months=1)
    while start_date <= end_date:
        key = start_date.strftime('%Y-%m')
        start_date += delta

        base[key] = {}

        for gender in Gender:
            base[key][gender] = 0

    return base
