from datetime import date
import typing as T

from flask import request as FlaskRequest
from pydantic import BaseModel, ValidationError as PyValidationError


class ValidationError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__()
        self.message = message
        self.status_code = status_code


class Request(BaseModel):
    @classmethod
    def from_request(cls, request: FlaskRequest) -> 'TRequest':
        raise NotImplementedError


TRequest = T.Type[Request]


class QueryRequestModel(Request):
    start_date: date
    end_date: date

    @classmethod
    def from_request(cls, request: FlaskRequest) -> TRequest:
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        try:
            req = cls(start_date=start_date, end_date=end_date)
        except PyValidationError:
            raise ValidationError(message="Missing or invalid query params", status_code=400)
        return req


