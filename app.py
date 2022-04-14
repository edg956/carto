from flask import Flask

from config import Config, settings
from geoapp.db import init
from geoapp.DTOs import ValidationError
from geoapp.handlers import query_blueprint, validation_error_handler


def setup(config: Config = settings):
    init(config)


app = Flask(__name__)

setup(settings)

app.register_blueprint(query_blueprint, url_prefix='/api')
app.register_error_handler(ValidationError, validation_error_handler)
