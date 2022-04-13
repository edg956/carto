import logging
import typing as T

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED
from pydantic import BaseModel

from config.config import Config, DatabaseConfig

logger = logging.getLogger(__name__)


PsycopgConnection = T.Type[T.Any]


class Database(BaseModel):
    config: T.Optional[DatabaseConfig]
    conn: T.Optional[PsycopgConnection]
    initialized: bool = False

    @property
    def name(self):
        if not self.config:
            return 'Unknown'

        return self.config.database

    @property
    def connection(self) -> PsycopgConnection:
        if not self.initialized:
            raise DatabaseNotInitialized
        return self.conn

    def shutdown(self):
        if self.initialized:
            self.conn.close()

    def set_autocommit(self, autocommit: bool):
        self.connection.commit()
        self.connection.autocommit = autocommit

    def init(self, config: Config):
        connection = init_conn(config)

        if self.initialized:
            self.conn.close()

        self.conn = connection
        self.config = config

        self.initialized = True


database = Database()


class DatabaseError(Exception):
    pass


class DatabaseInitializationError(DatabaseError):
    pass


class DatabaseNotInitialized(DatabaseError):
    pass


def init_conn(config: DatabaseConfig) -> PsycopgConnection:
    logger.info("Initializing to database")

    create_database_if_not_exists(config)

    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        database=config.database,
        password=config.password
    )

    if not conn:
        raise DatabaseInitializationError

    conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)

    return conn


def create_database_if_not_exists(config: DatabaseConfig):
    logger.info("Initializing to database")

    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password
    )

    if not conn:
        raise DatabaseInitializationError

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (config.database,))
        exists = bool(cur.fetchone())

        if not exists:
            cur.execute(f"CREATE DATABASE {config.database};")

    conn.commit()
    conn.close()


def init_tables(database: Database):
    conn = database.connection

    logger.info("Loading SQL Script")

    with open('config/db.sql', 'r') as f:
        sql = f.read()

    logger.info("Initializing Database")
    with conn.cursor() as cur:
        cur.execute(sql)


def init(config: DatabaseConfig) -> Database:
    global database

    database.init(config)

    init_tables(database)


def teardown():
    global database
    database.shutdown()


def destroy(config: DatabaseConfig):
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password
    )

    if not conn:
        raise DatabaseInitializationError

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (config.database,))
        exists = bool(cur.fetchone())

        if not exists:
            cur.execute(f"DROP DATABASE {config.database};")

    conn.commit()
    conn.close()
