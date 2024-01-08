"""Module that contains extra models for the REST API."""

from pydantic import BaseModel


class Version(BaseModel):
    """Version information for the REST API.

    Attributes:
        version: The version of the REST API.
        python_version: The version of Python used by the REST API.
        internal_dependencies: A dictionary of internal dependencies
            where the key is the name of the dependency and the value is the
            corresponding version.
        external_dependencies: A dictionary of external dependencies
            where the key is the name of the dependency and the value is the
            corresponding version.
    """

    version: str
    python_version: str | None = None
    internal_dependencies: dict[str, str] | None = None
    external_dependencies: dict[str, str] | None = None


class AuthenticationDetails(BaseModel):
    """Authentication details for the REST API.

    Attributes:
        username: The username for the user.
        password: The password for the user.
        second_factor: The second factor for authentication, if applicable.
    """

    username: str
    password: str
    second_factor: str | None = None
