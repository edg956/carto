import typing as T

from flask import Blueprint, request

from geoapp.DTOs import QueryRequestModel
from geoapp.services import PostgresQueryService

# Services to use in handlers
query_service = PostgresQueryService()


query_blueprint = Blueprint('dashboard', __name__)


@query_blueprint.route('/map', methods=('GET',))
def get_map() -> T.Tuple:
    query: QueryRequestModel = QueryRequestModel.from_request(request)
    return query_service.get_map(query.start_date, query.end_date), 200


@query_blueprint.route('/turnover', methods=('GET',))
def get_turnover() -> T.Tuple:
    query: QueryRequestModel = QueryRequestModel.from_request(request)
    return query_service.get_turnover(query.start_date, query.end_date), 200


@query_blueprint.route('/turnover/age-gender', methods=('GET',))
def get_turnover_by_age_and_gender() -> T.Tuple:
    query: QueryRequestModel = QueryRequestModel.from_request(request)
    return query_service.get_turnover_by_age_and_gender(query.start_date, query.end_date), 200


@query_blueprint.route('/turnover/time-gender', methods=('GET',))
def get_turnover_by_time_and_gender() -> T.Tuple:
    query: QueryRequestModel = QueryRequestModel.from_request(request)
    return query_service.get_turnover_by_time_and_gender(query.start_date, query.end_date), 200


def validation_error_handler(ex):
    return {"message": ex.message}, ex.status_code
