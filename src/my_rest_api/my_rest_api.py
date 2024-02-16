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
        config = AppConfig()

        # MyData configuration
        self._db_string: str = config.database_str
        self._db_args: dict[str, Any] | None = config.database_args
        self._service_user = config.service_user
        self._service_password = config.service_password

    def _db_is_created(self) -> bool:
        """Return True if the database is created.

        Returns:
            bool: True if the database is created, False otherwise.
        """
        return self.data.database_engine is not None

    def _create_my_data(self) -> None:
        """Create the MyData object.

        The MyData object is used to communicate with the persistent data
        store. Using this method, the database object can be created.
        """
        self.data.configure(
            db_connection_str=self._db_string,
            database_args=self._db_args,
            service_username=self._service_user,
            service_password=self._service_password)
        self.data.create_engine(force=True)

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
