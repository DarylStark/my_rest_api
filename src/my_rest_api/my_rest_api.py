"""Module that contains the MyRESTAPI class."""

from typing import Optional
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
        self.data: MyData = MyData()
        self.config = AppConfig()

    def configure_my_data(
            self,
            database_str: str | None = None,
            create_tables: bool = False,
            create_init_data: bool = False) -> None:
        """Return the MyData object.

        The MyData object is used to communicate with the persistent data
        store. Using this method, the database connection string can be set.

        Args:
            database_str: the database string to configure. If this is not
                specified, the database string from the config file will be
                used.
            create_tables: if True, the database tables will be created.
            create_init_data: if True, initial data will be created.
        """
        database_str = database_str or self.config.database_str
        self.data.configure(db_connection_str=database_str)
        self.data.create_engine(force=False)

        if create_tables:
            self.data.create_db_tables()
        if create_init_data:
            self.data.create_init_data()
