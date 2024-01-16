"""Module that contains the MyRESTAPI class."""

from typing import Any, Optional
from my_data.my_data import MyData

from .app_config import AppConfig


class MyRESTAPI:
    """Class that represents a REST API.

    Contains variables and objects to use during endpoint execution. Can, and
    should be used, asa a singleton.
    """

    _instance: Optional['MyRESTAPI'] = None

    @classmethod
    def get_instance(cls) -> 'MyRESTAPI':
        """Return the singleton instance of this class.

        Makes this class a singleton.

        Returns:
            A unique instane of MyRESTAPI.
        """
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """Initialize the class."""
        # Objects for the complete application
        self.data: MyData = MyData()
        self.config = AppConfig()

        # Database configuration
        self._db_string: str = self.config.database_str
        self._db_args: dict[str, Any] | None = None
        self._create_tables: bool = False
        self._create_init_data: bool = False

    def _db_is_created(self) -> bool:
        """Return True if the database is created.

        Returns:
            bool: True if the database is created, False otherwise.
        """
        return self.data.database_engine is not None

    def configure_my_data(
            self,
            database_str: str | None = None,
            database_args: dict[str, Any] | None = None,
            create_tables: bool = False,
            create_init_data: bool = False) -> None:
        """Set the database configuration.

        The MyData object is used to communicate with the persistent data
        store. Using this method, the database can be configured.

        Args:
            database_str: the database string to configure. If this is not
                specified, the database string from the config file will be
                used.
            database_args: the database arguments to configure. If this is not
                specified, the database arguments from the config file will be
                used.
            create_tables: if True, the database tables will be created.
            create_init_data: if True, initial data will be created.
        """
        self._db_string = database_str or self.config.database_str
        self._db_args = database_args or self.config.database_args
        self._create_tables = create_tables
        self._create_init_data = create_init_data

    def _create_my_data(self) -> None:
        """Create the MyData object.

        The MyData object is used to communicate with the persistent data
        store. Using this method, the database object can be created.
        """
        self.data.configure(
            db_connection_str=self._db_string,
            database_args=self._db_args)
        self.data.create_engine(force=True)

        if self._create_tables:
            self.data.create_db_tables()
        if self._create_init_data:
            self.data.create_init_data()

    @property
    def my_data(self) -> MyData:
        """Return the MyData object.

        The MyData object is used to communicate with the persistent data
        store.

        Returns:
            MyData: the MyData object.
        """
        if not self._db_is_created():
            self._create_my_data()
        return self.data
