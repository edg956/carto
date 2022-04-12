from datetime import date
import pytest

from geoapp import services


@pytest.fixture
def date_range():
    return date(2015, 1, 1), date(2015, 1, 31)


class TestMapService:
    @pytest.fixture
    def service():
        service = services.InMemoryQueryService(
            data=(
                "amount,p_month,p_age,p_gender,postal_code_id,id,code,the_geom\n"
                "10,2015-01-01,<=24,M,6055,4627,28008,dummy-geom\n"
                "10,2015-01-01,25-34,M,6055,8095,28008,dummy-geom\n"
                "10,2015-01-01,<=24,F,6055,1117,28008,dummy-geom\n"
                "10,2015-01-01,25-34,F,6055,10616,28008,dummy-geom\n"
                "10,2015-01-01,35-44,F,6055,6383,28008,dummy-geom\n"
            )
        )

    @pytest.fixture
    def date_range():
        return date(2015, 1, 1), date(2015, 1, 31)

    def test_get_map_returns_one_postalcode(self, service, date_range):
        map_ = service.get_map(*date_range)
        assert len(map_) == 1       # TODO: define

    def test_get_map_returns_appropriate_aggregate_by_age_and_gender(self, service, date_range):
        map_ = service.get_map(*date_range)
        agg = map_[0]

        assert '<=24' in agg
        assert 'M' in agg['<=24']
        assert 'F' in agg['<=24']
        assert '25-34' in agg
        assert 'M' in agg['25-34']
        assert 'F' in agg['25-34']
        assert '35-44' in agg
        assert 'F' in agg['35-44']
        assert 'M' not in agg['35-44']

        assert agg['<=24']['F'] == 10
        assert agg['<=24']['M'] == 10
        assert agg['25-34']['F'] == 10
        assert agg['25-34']['M'] == 10
        assert agg['35-44']['F'] == 10
