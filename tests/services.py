from datetime import date
import pytest

from geoapp import services


@pytest.fixture
def date_range():
    return date(2015, 1, 1), date(2015, 1, 31)


class TestMapService:
    @pytest.fixture(scope="class")
    def service(self, database):
        service = services.PostgresQueryService(database)

        with database.atomic(effect='rollback'):
            database.execute_statement(
                query=(
                    "INSERT INTO PostalCodes (the_geom, code, id) VALUES "
                    f"{','.join(['(%s, %s, %s)'] * 2)}"
                ),
                params=(
                    "dummy-geom", 28668, 6179,
                    "other-geom", 28932, 6061
                ),
            )
            database.execute_statement(
                query=(
                    "INSERT INTO Payments (amount, p_month, p_age, p_gender, postal_code_id, id) VALUES "
                    f"{','.join(['(%s, %s, %s, %s, %s, %s)'] * 5)}"
                ),
                params=(
                    10, "1/1/2015", "<=24", "M", 6179, 1117,
                    10, "1/2/2015", "<=24", "M", 6179, 4627,
                    10, "1/1/2015", "25-34", "F", 6061, 10616,
                    10, "2/1/2015", "25-34", "M", 6179, 8095,
                    10, "2/1/2015", "35-44", "F", 6061, 6383,
                ),
            )

            yield service


    @pytest.fixture()
    def date_range(self):
        return date(2015, 1, 1), date(2015, 2, 28)

    def test_get_map_returns_one_postalcode(self, service, date_range):
        map_ = service.get_map(*date_range)
        assert 'results' in map_
        print(map_)
        assert len(map_['results']) == 2

    def test_get_map_returns_appropriate_aggregate_by_age_and_gender(self, service, date_range):
        map_ = service.get_map(*date_range)

        assert 'results' in map_
        results = list(sorted(map_['results'], key=lambda x: x['geometry']))

        postcode = results[0]

        assert postcode['geometry'] == 'dummy-geom'
        agg = postcode['turnover']

        assert int(agg['<=24']['M']) == 20
        assert int(agg['<=24']['F']) == 0
        assert int(agg['25-34']['M']) == 10
        assert int(agg['25-34']['F']) == 0
        assert int(agg['35-44']['F']) == 0
        assert int(agg['35-44']['M']) == 0

        postcode = results[1]

        assert postcode['geometry'] == 'other-geom'
        agg = postcode['turnover']

        assert int(agg['<=24']['M']) == 0
        assert int(agg['<=24']['F']) == 0
        assert int(agg['25-34']['M']) == 0
        assert int(agg['25-34']['F']) == 10
        assert int(agg['35-44']['F']) == 10
        assert int(agg['35-44']['M']) == 0

    def test_get_turnover_total_returns_50(self, service, date_range):
        turnover = service.get_turnover(*date_range)
        
        assert 'results' in turnover
        assert int(turnover['results']) == 50

    def test_get_turnover_by_age_and_gender_returns_appropriate_results(self, service, date_range):
        turnover = service.get_turnover_by_age_and_gender(*date_range)

        assert 'results' in turnover
        results = turnover['results']

        assert int(results['<=24']['M']) == 20
        assert int(results['<=24']['F']) == 0
        assert int(results['25-34']['M']) == 10
        assert int(results['25-34']['F']) == 10
        assert int(results['35-44']['F']) == 10
        assert int(results['35-44']['M']) == 0

    def test_get_turnover_by_time_and_gender_returns_appropriate_results(self, service, date_range):
        turnover = service.get_turnover_by_time_and_gender(*date_range)

        assert 'results' in turnover
        results = turnover['results']

        assert int(results['2015-01']['M']) == 20
        assert int(results['2015-01']['F']) == 10
        assert int(results['2015-02']['F']) == 10
        assert int(results['2015-02']['M']) == 10
