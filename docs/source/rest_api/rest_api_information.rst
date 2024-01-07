REST API information
====================

In the root of the API are the endpoints to retrieve information about the API itself. There is no authentication required to access these endpoints.

REST API version
----------------

The version of the API is available at the root of the API. It is available at the ``/version`` endpoint and it will return a JSON object with the version information about the REST API and the dependencies it uses.

.. code-block:: json

    {
        "version": "1.0.0-dev",
        "python_version": "3.10.13",
        "internal_dependencies": null,
        "external_dependencies": {
            "fastapi": "0.108.0",
            "pydantic": "2.5.3"
        }
    }