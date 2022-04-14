import abc
import csv
import logging
import typing as T

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED
from tenacity import Retrying, wait_exponential, stop_after_attempt

from config.config import Config, DatabaseConfig, settings

logger = logging.getLogger(__name__)


PsycopgConnection = T.Type[T.Any]


class DatabaseError(Exception):
    pass


class DatabaseInitializationError(DatabaseError):
    pass


class DatabaseNotInitialized(DatabaseError):
    pass


class InvalidDatabaseClass(Exception):
    pass


class Database(abc.ABC):
    def __init__(self, config: DatabaseConfig = None):
        self.config: config

        if config:
            self.init(config)

    @property
    def name(self) -> str:
        if not self.config:
            return 'Unknown'

        return self.config.database

    @abc.abstractmethod
    def execute_query(self, query: str, params: str) -> T.List:
        raise NotImplementedError

    @abc.abstractmethod
    def execute_statement(self, query: str, params: T.Tuple = None):
        raise NotImplementedError

    @abc.abstractmethod
    def shutdown(self):
        raise NotImplementedError

    @abc.abstractmethod
    def init(self, config: Config):
        pass

    @abc.abstractmethod
    def atomic(self, effect: str = 'commit'):
        raise NotImplementedError

    @abc.abstractmethod
    def destroy(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create_database_if_not_exists(self):
        raise NotImplementedError

    @abc.abstractmethod
    def teardown(self):
        raise NotImplementedError

    @abc.abstractmethod
    def destroy(self):
        raise NotImplementedError


class PostgresDatabase(Database):
    def __init__(self, config: DatabaseConfig = None):
        self._conn: T.Optional[PsycopgConnection] = None
        super().__init__(config)

    def shutdown(self):
        self._conn.rollback()
        self._conn.close()

    def _set_autocommit(self, autocommit: bool):
        self._conn.commit()
        self._conn.autocommit = autocommit

    def init(self, config: Config):
        if self._conn:
            self._conn.close()

        self.config = config

        for attempt in Retrying(
                stop=stop_after_attempt(4),
                wait=wait_exponential(),
                reraise=True
        ):
            with attempt:
                self._conn = self._init_conn()

    def atomic(self, effect: str = 'commit'):
        assert effect in ['commit', 'rollback'], f"Effect must be either `commit` or `rollback`. Got `{effect}`"

        class atomic:
            def __enter__(self_):
                self_._old_state = self._conn.autocommit
                self._set_autocommit(False)

            def __exit__(self_, *args, **kwargs):
                self._set_autocommit(self_._old_state)
                getattr(self._conn, effect)()
        
        return atomic()

    def execute_query(self, query: str, params: T.Tuple = None) -> T.List[T.Tuple]:
        with self._conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def execute_statement(self, query: str, params: T.Tuple = None):
        with self._conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)

    def _init_conn(self) -> PsycopgConnection:
        logger.info("Initializing to database")

        self.create_database_if_not_exists()

        conn = psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            database=self.config.database,
            password=self.config.password
        )

        if not conn:
            raise DatabaseInitializationError

        conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)

        return conn

    def create_database_if_not_exists(self):
        logger.info("Initializing to database")

        conn = psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password
        )

        if not conn:
            raise DatabaseInitializationError

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (self.config.database,))
            exists = bool(cur.fetchone())

            if not exists:
                cur.execute(f"CREATE DATABASE {self.config.database};")

        conn.commit()
        conn.close()

    def teardown(self):
        self.shutdown()
        self.destroy()

    def destroy(self):
        conn = psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password
        )

        if not conn:
            raise DatabaseInitializationError

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (self.config.database,))
            exists = bool(cur.fetchone())

            if exists:
                cur.execute(f"DROP DATABASE {self.config.database};")

        conn.commit()
        conn.close()


def init_tables(db: Database, config: Config):
    logger.info("Loading SQL Script")

    with open('config/db.sql', 'r') as f:
        sql = f.read()

    logger.info("Initializing Database")
    db.execute_statement(sql)

    if config.test:
        return

    logger.info("Loading data")
    with db.atomic():
        res = db.execute_query("SELECT COUNT(*) FROM PostalCodes")
        if not res[0][0]:
            load_database(db, "PostalCodes", config.data.postalcodes)

        res = db.execute_query("SELECT COUNT(*) FROM Payments")
        if not res[0][0]:
            load_database(db, "Payments", config.data.payments)


def init(config: Config) -> Database:
    global database

    if config.test:
        config.db_config.database = f"test_{config.db_config.database}"

    database.init(config.db_config)

    init_tables(database, config)


def load_database(db: Database, table_name: str, path: str):
    db.execute_statement(f"COPY {table_name} FROM '{path}' csv header")


def _csv_lines(path: str) -> T.Iterable:
    with open(path) as f:
        reader = csv.reader(f)

        # Skip header
        next(reader)

        for row in reader:
            yield row


if settings.db_config.database_class not in locals():
    raise InvalidDatabaseClass(f"Database class {settings.db_config.database_class} not found")

database_class = locals().get(settings.db_config.database_class)
database = database_class()
