import logging
import psycopg2

from config.config import DatabaseConfig

logger = logging.getLogger(__name__)


def init_db(config: DatabaseConfig):
    logger.info("Loading SQL Script")

    with open('config/db.sql', 'r') as f:
        sql = f.read()

    logger.info("Connecting to database")
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        database=config.database,
        user=config.user,
        password=config.password
    )

    logger.info("Initializing Database")
    with conn.cursor() as cur:
        cur.execute(sql)
