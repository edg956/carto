from datetime import date
import pytest
from config.config import DatabaseConfig

from geoapp import services
from config import settings


@pytest.fixture
def date_range():
    return date(2015, 1, 1), date(2015, 1, 31)


class TestMapService:
    @pytest.fixture(scope="class")
    def service(self, database):
        service = services.PostgresQueryService()

        with service.db.atomic(effect='rollback'):

            yield service


    @pytest.fixture()
    def date_range(self):
        return date(2015, 1, 1), date(2015, 2, 28)

    def test_get_map_returns_one_postalcode(self, service, date_range):
        map_ = service.get_map(*date_range)
        assert 'results' in map_
        assert len(map_['results']) == 2

    def test_get_map_returns_appropriate_aggregate_by_age_and_gender(self, service, date_range):
        map_ = service.get_map(*date_range)

        assert 'results' in map_
        results = map_['results']

        postcode = results[0]

        assert postcode['geometry'] == 'dummy-geom'
        agg = postcode['turnover']

        assert agg['<=24']['M'] == 20
        assert agg['<=24']['F'] == 0
        assert agg['25-34']['M'] == 10
        assert agg['25-34']['F'] == 0
        assert agg['35-44']['F'] == 0
        assert agg['35-44']['M'] == 0

        postcode = results[1]

        assert postcode['geometry'] == 'other-geom'
        agg = postcode['turnover']

        assert agg['<=24']['M'] == 0
        assert agg['<=24']['F'] == 0
        assert agg['25-34']['F'] == 10
        assert agg['25-34']['M'] == 0
        assert agg['35-44']['F'] == 10
        assert agg['35-44']['M'] == 0

    def test_get_turnover_total_returns_50(self, service, date_range):
        turnover = service.get_turnover(*date_range)
        
        assert 'results' in turnover
        assert turnover['results'] == 50

    def test_get_turnover_by_age_and_gender_returns_appropriate_results(self, service, date_range):
        turnover = service.get_turnover_by_age_and_gender(*date_range)

        assert 'results' in turnover
        results = turnover['results']

        assert results['<=24']['M'] == 20
        assert results['<=24']['F'] == 0
        assert results['25-34']['M'] == 10
        assert results['25-34']['F'] == 10
        assert results['35-44']['F'] == 10
        assert results['35-44']['M'] == 0

    def test_get_turnover_by_time_and_gender_returns_appropriate_results(self, service, date_range):
        turnover = service.get_turnover_by_time_and_gender(*date_range)

        assert 'results' in turnover
        results = turnover['results']

        assert results['2015-01']['M'] == 20
        assert results['2015-01']['F'] == 10
        assert results['2015-02']['F'] == 10
        assert results['2015-02']['M'] == 10
