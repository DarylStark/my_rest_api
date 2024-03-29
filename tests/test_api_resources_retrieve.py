"""Tests for retrieving resources using the REST API."""

import pytest
from fastapi.testclient import TestClient


def create_endpoint_url(
    endpoint: str,
    arguments: dict[str, str | int] | None = None,
    id: int | None = None,
) -> str:
    """Create the endpoint URL.

    Args:
        endpoint: the endpoint.
        arguments: the arguments for the endpoint. Can be omitted if there are
            no arguments.
        id: a ID to grab.

    Returns:
        The endpoint URL.
    """
    args_string = ''
    if arguments and len(arguments):
        args_string = '&'.join(
            [f'{argument}={value}' for argument, value in arguments.items()]
        )
    if id:
        endpoint += f'/{id}'
    return f'/resources/{endpoint}?{args_string}'


@pytest.mark.parametrize(
    'endpoint, id',
    (
        ('users', 1),
        ('tags', 1),
        ('user_settings', 1),
        ('api_clients', 1),
        ('api_tokens', 1),
    ),
)
def test_retrieve_by_id(
    api_client: TestClient,
    endpoint: str,
    id: int,
) -> None:
    """Test retrieving resources by id.

    Happy path test; should always be a success and return one item.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        id: the ID to grab.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'
    # Set the endpoint
    endpoint = create_endpoint_url(endpoint, id=id)

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )

    # Validate the answer
    assert result.status_code == 200

    # Check if we have the three required fields: `id`, `created`, and
    # `updated`
    data = result.json()
    assert data['id'] == id
    assert data['created'] is not None
    assert data['updated'] is not None
    assert data['uri'] is not None


@pytest.mark.parametrize(
    'endpoint, id',
    (
        ('users', 999),
        ('tags', 999),
        ('user_settings', 999),
        ('api_clients', 999),
        ('api_tokens', 999),
    ),
)
def test_retrieve_by_wrong_id(
    api_client: TestClient,
    endpoint: str,
    id: int,
) -> None:
    """Test retrieving resources by wrong id.

    Unhappy path test; should always return a 404.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        id: the ID to grab.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'
    # Set the endpoint
    endpoint = create_endpoint_url(endpoint, id=id)

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )

    # Validate the answer
    assert result.status_code == 404


@pytest.mark.parametrize(
    'endpoint, expected_count',
    (
        ('users', 4),
        ('tags', 3),
        ('user_settings', 3),
        ('api_clients', 1),
        ('api_tokens', 2),
    ),
)
def test_retrieval_short_lived(
    api_client: TestClient,
    endpoint: str,
    expected_count: int,
) -> None:
    """Test that the retrieval endpoints work with a short lived token.

    Happy path test; should always be a success and return some data. We test
    retrieving data without any filters for all resources that should return
    data with a short lived token.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        expected_count: the expected count of items.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'
    # Set the endpoint
    endpoint = create_endpoint_url(endpoint)

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response['resources']) == expected_count


@pytest.mark.parametrize('endpoint, expected_count', (('users', 1),))
def test_retrieval_short_lived_normal_user(
    api_client: TestClient,
    endpoint: str,
    expected_count: int,
) -> None:
    """Test that the retrieval endpoints work with a short lived token.

    Happy path test; should always be a success and return some data. We test
    retrieving data without any filters for all resources that should return
    data with a short lived token. We test this with a token for normal users
    that only have access to their own data. We test if we only retrieve the
    data for the normal user.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        expected_count: the expected count of items.
    """
    _token = 'pabq1d533eMucNPr5pHPuDMqxKRw1SE0'
    # Set the endpoint
    endpoint = create_endpoint_url('users')

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response['resources']) == expected_count
    assert response['resources'][0]['username'] == 'normal.user'


@pytest.mark.parametrize(
    'endpoint, expected_count',
    (
        ('users', 4),
        ('tags', 3),
        ('user_settings', 3),
        ('api_tokens', 2),
    ),
)
def test_retrieval_long_lived(
    api_client: TestClient,
    endpoint: str,
    expected_count: int,
) -> None:
    """Test that the retrieval endpoints work with a long lived token.

    Happy path test; should always be a success and return some data. We test
    retrieving data without any filters for all resources that should return
    data with a long lived token.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        expected_count: the expected count of items.
    """
    _token = 'MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL'
    # Set the endpoint
    endpoint = create_endpoint_url(endpoint)

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response['resources']) == expected_count


@pytest.mark.parametrize(
    'endpoint',
    ('api_clients',),
)
def test_retrieval_long_lived_invaild_endpoint(
    api_client: TestClient,
    endpoint: str,
) -> None:
    """Test that the retrieval endpoints work with a long lived token.

    Unhappy path test; we test if endpoints that require a short lived token
    fail when given a long lived token.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
    """
    _token = 'MHxHL4HrmmJHbAR1b0gV4OkpuEsxxmRL'
    # Set the endpoint
    endpoint = create_endpoint_url(endpoint)

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint',
    (
        ('users'),
        ('tags'),
        ('user_settings'),
        ('api_tokens'),
    ),
)
def test_retrieval_long_lived_missing_scope(
    api_client: TestClient, endpoint: str
) -> None:
    """Test retrieval with a long lived token without the correct scopes.

    Unhappy path test; we test if endpoints that can work with a long lived
    token fail when the needed scope is missing.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
    """
    _token = '6VZGMOdNUAhCzYhipVJJjHTsYIzwBrlg'
    # Set the endpoint
    endpoint = create_endpoint_url(endpoint)

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint',
    (
        ('users'),
        ('tags'),
        ('user_settings'),
        ('api_clients'),
        ('api_tokens'),
    ),
)
def test_retrieval_missing_token(
    api_client: TestClient, endpoint: str
) -> None:
    """Test retrieval without a token.

    Unhappy path test; we test if endpoints fail if we don't specify a token.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
    """
    # Set the endpoint
    endpoint = create_endpoint_url(endpoint)

    # Do the request
    result = api_client.get(
        endpoint,
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint',
    (
        ('users'),
        ('tags'),
        ('user_settings'),
        ('api_clients'),
        ('api_tokens'),
    ),
)
def test_retrieval_invalid_token(
    api_client: TestClient, endpoint: str
) -> None:
    """Test retrieval with a invalid token.

    Unhappy path test; we test if endpoints fail if we give a invalid token.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
    """
    # Set the endpoint
    endpoint = create_endpoint_url(endpoint)

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': 'invalid_token'},
    )

    # Validate the answer
    assert result.status_code == 401


@pytest.mark.parametrize(
    'endpoint, expected_count, flt',
    (
        ('users', 1, 'id==1'),
        ('users', 3, 'id!=1'),
        ('users', 1, 'id<2'),
        ('users', 3, 'id>1'),
        ('users', 2, 'id<=2'),
        ('users', 3, 'id>=2'),
        ('users', 1, 'username==root'),
        ('users', 1, 'username==root,id==1'),
        ('users', 0, 'username==root,id==2'),
        ('users', 2, 'username=contains=normal'),
        ('users', 2, 'username=contains=normal,email=contains=normal'),
        ('users', 3, 'username=!contains=service'),
        ('users', 1, 'fullname==root'),
        ('users', 2, 'fullname=contains=normal'),
        ('users', 3, 'fullname=!contains=service'),
        ('users', 1, 'email==normal_user@example.com'),
        ('users', 2, 'email=contains=normal_user'),
        ('users', 3, 'email=!contains=service'),
        ('tags', 1, 'id==1'),
        ('tags', 2, 'id!=1'),
        ('tags', 2, 'id<3'),
        ('tags', 2, 'id>1'),
        ('tags', 3, 'id<=3'),
        ('tags', 2, 'id>=2'),
        ('tags', 2, 'id>=2,id<=4'),
        ('tags', 1, 'title==root_tag_1'),
        ('tags', 1, 'title=contains=tag_1'),
        ('tags', 2, 'title=!contains=tag_1'),
        ('user_settings', 1, 'id==1'),
        ('user_settings', 2, 'id!=1'),
        ('user_settings', 2, 'id>1'),
        ('user_settings', 2, 'id<3'),
        ('user_settings', 2, 'id>=2'),
        ('user_settings', 2, 'id<=2'),
        ('user_settings', 1, 'setting==root_test_setting_1'),
        ('user_settings', 3, 'setting=contains=root_test_setting'),
        ('user_settings', 2, 'setting=!contains=_1'),
        ('user_settings', 1, 'value==test_value_1'),
        ('user_settings', 3, 'value=contains=test_value'),
        ('user_settings', 2, 'value=!contains=_1'),
        ('api_clients', 1, 'id==1'),
        ('api_clients', 0, 'id!=1'),
        ('api_clients', 0, 'id>1'),
        ('api_clients', 1, 'id<3'),
        ('api_clients', 0, 'id>=2'),
        ('api_clients', 1, 'id<=2'),
        ('api_clients', 1, 'app_name==root_api_client_1'),
        ('api_clients', 1, 'app_name=contains=api_client'),
        ('api_clients', 0, 'app_name=!contains=api_client'),
        ('api_clients', 1, 'app_publisher==root_api_client_1_publisher'),
        ('api_clients', 1, 'app_publisher=contains=publisher'),
        ('api_clients', 0, 'app_publisher=!contains=publisher'),
        ('api_tokens', 1, 'id==1'),
        ('api_tokens', 1, 'id!=1'),
        ('api_tokens', 1, 'id>1'),
        ('api_tokens', 1, 'id<2'),
        ('api_tokens', 2, 'id>=1'),
        ('api_tokens', 2, 'id<=2'),
        ('api_tokens', 1, 'title==root_long_lived_token_all_permissions'),
        ('api_tokens', 1, 'title=contains=long_lived'),
        ('api_tokens', 1, 'title=!contains=long_lived'),
        ('api_tokens', 1, 'api_client_id==1'),
        ('api_tokens', 0, 'api_client_id!=1'),
        ('api_tokens', 1, 'api_client_id==null'),
        ('api_tokens', 1, 'api_client_id!=null'),
    ),
)
def test_retrieval_short_lived_with_valid_filters(
    api_client: TestClient,
    endpoint: str,
    expected_count: int,
    flt: str | None,
) -> None:
    """Test that the retrieval endpoint works with valid filters.

    Happy path test; should always be a success and return some data. We test
    all the possible filters for the retrieval endpoint for all the possible
    resources.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        expected_count: the expected count of items.
        flt: the filter to use.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'
    # Compile the arguments for the endpoint
    args: dict[str, str | int] = {}
    if flt:
        args['filter'] = flt

    # Create the endpoint string
    endpoint = create_endpoint_url(endpoint, args)

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response['resources']) == expected_count


@pytest.mark.parametrize(
    'endpoint, flt',
    (
        ('users', 'id==test'),
        ('users', 'id=>1'),
        ('users', 'invalid_filter'),
        ('tags', 'title=like=tag_1'),
        ('tags', 'title=!like=tag_1'),
        ('tags', 'invalid_filter'),
        ('user_settings', 'settings=!contains=_1'),
        ('user_settings', 'value=!_1'),
        ('user_settings', 'invalid_filter'),
        ('api_clients', 'id=contains=1'),
        ('api_clients', 'id<>0'),
        ('api_clients', 'invalid_filter'),
        ('api_tokens', 'id=contains=1'),
        ('api_tokens', 'id<>0'),
        ('api_tokens', 'invalid_filter'),
    ),
)
def test_retrieval_short_lived_with_invalid_filters(
    api_client: TestClient,
    endpoint: str,
    flt: str | None,
) -> None:
    """Test that the retrieval endpoint works with invalid filters.

    Unhappy path test; should always fail with error 400.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        flt: the filter to use.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'
    # Compile the arguments for the endpoint
    args: dict[str, str | int] = {}
    if flt:
        args['filter'] = flt

    # Create the endpoint string
    endpoint = create_endpoint_url(endpoint, args)

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )

    # Validate the answer
    assert result.status_code == 400


@pytest.mark.parametrize(
    'endpoint, sort_field',
    (
        ('users', 'username'),
        ('users', 'role'),
        ('tags', 'title'),
        ('tags', 'id'),
        ('user_settings', 'setting'),
        ('user_settings', 'value'),
        ('api_clients', 'app_name'),
        ('api_clients', 'app_publisher'),
        ('api_tokens', 'id'),
        ('api_tokens', 'title'),
        ('api_tokens', 'created'),
        ('api_tokens', 'expires'),
    ),
)
def test_retrieval_short_lived_with_valid_sort_field(
    api_client: TestClient, endpoint: str, sort_field: str
) -> None:
    """Test that the retrieval endpoint works with valid sort field.

    Happy test path: should return one item.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        sort_field: the field to sort on.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'

    # Create the endpoint string
    endpoint = create_endpoint_url(
        endpoint, {'sort': sort_field, 'page_size': 1, 'page': 1}
    )

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response['resources']) == 1


@pytest.mark.parametrize(
    'endpoint, sort_field, first_id',
    (
        ('users', '^id', 4),
        ('tags', '^id', 3),
        ('user_settings', '^id', 3),
        ('api_tokens', '^id', 2),
        ('users', 'id', 1),
        ('tags', 'id', 1),
        ('user_settings', 'id', 1),
        ('api_tokens', 'id', 1),
    ),
)
def test_retrieval_short_lived_with_valid_descending_sort_field(
    api_client: TestClient, endpoint: str, sort_field: str, first_id: int
) -> None:
    """Test that the retrieval endpoint works with valid sort field.

    Happy test path: should return one item with the correct id

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        sort_field: the field to sort on.
        first_id: the first id to expect.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'

    # Create the endpoint string
    endpoint = create_endpoint_url(
        endpoint, {'sort': sort_field, 'page_size': 1, 'page': 1}
    )

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response['resources']) == 1
    assert response['resources'][0]['id'] == first_id


def test_retrieval_short_lived_with_valid_sort_fields(
    api_client: TestClient,
) -> None:
    """Test that the retrieval endpoint works with valid sort fields.

    Happy test path: should return in the correct order

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        sort_field: the field to sort on.
        first_id: the first id to expect.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'

    # Create the endpoint string
    endpoint = create_endpoint_url('tags', {'sort': 'color,^id'})

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response['resources']) == 3
    assert response['resources'][0]['id'] == 3
    assert response['resources'][1]['id'] == 1
    assert response['resources'][2]['id'] == 2


@pytest.mark.parametrize(
    'endpoint, sort_field',
    (
        ('users', 'uname'),
        ('users', '_id'),
        ('users', 'password_hash'),
        ('tags', 'name'),
        ('tags', '!title'),
        ('user_settings', 'v'),
        ('user_settings', 'wrong_field'),
        ('api_clients', 'token'),
        ('api_clients', 'invalid_field'),
        ('api_tokens', 'token'),
        ('api_tokens', 'invalid_field'),
    ),
)
def test_retrieval_short_lived_with_invalid_sort_field(
    api_client: TestClient, endpoint: str, sort_field: str
) -> None:
    """Test that the retrieval endpoint works with invalid sort field.

    Unhappy test path: should always return error 400.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        sort_field: the field to sort on.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'

    # Create the endpoint string
    endpoint = create_endpoint_url(
        endpoint, {'sort': sort_field, 'page_size': 1, 'page': 1}
    )

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )

    # Validate the answer
    assert result.status_code == 400


@pytest.mark.parametrize(
    'endpoint, page, page_size, expected_count,  next_link, prev_link',
    (
        ('users', 1, 1, 1, True, False),
        ('users', 1, 2, 2, True, False),
        ('users', 1, 3, 3, True, False),
        ('users', 1, 4, 4, False, False),
        ('users', 2, 1, 1, True, True),
        ('users', 2, 2, 2, False, True),
        ('users', 2, 3, 1, False, True),
        ('tags', 1, 1, 1, True, False),
        ('tags', 2, 1, 1, True, True),
        ('tags', 3, 1, 1, False, True),
        ('tags', 1, 2, 2, True, False),
        ('tags', 2, 2, 1, False, True),
        ('tags', 1, 3, 3, False, False),
        ('user_settings', 1, 1, 1, True, False),
        ('user_settings', 2, 1, 1, True, True),
        ('user_settings', 3, 1, 1, False, True),
        ('user_settings', 1, 2, 2, True, False),
        ('user_settings', 2, 2, 1, False, True),
        ('user_settings', 1, 3, 3, False, False),
        ('api_clients', 1, 1, 1, False, False),
        ('api_clients', 1, 2, 1, False, False),
        ('api_tokens', 1, 1, 1, True, False),
        ('api_tokens', 2, 1, 1, False, True),
    ),
)
def test_retrieval_short_lived_with_pagination(
    api_client: TestClient,
    endpoint: str,
    page: int,
    page_size: int,
    expected_count: int,
    next_link: bool,
    prev_link: bool,
) -> None:
    """Test that the retrieval endpoint works with pagination.

    Happy path test; should always be a success and return some data. We test
    retrieving data and checking if all the page information is correct.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        page: the page to retrieve.
        page_size: the page size.
        expected_count: the expected count of items.
        next_link: whether there should be a "next" link.
        prev_link: whether there should be a "previous" link.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'
    # Set the endpoint
    endpoint = create_endpoint_url(
        endpoint, {'page_size': page_size, 'page': page}
    )

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response['resources']) == expected_count
    assert ('next' in result.links) == next_link
    assert ('prev' in result.links) == prev_link
    assert 'first' in result.links
    assert 'last' in result.links


@pytest.mark.parametrize(
    'endpoint, page_size',
    (
        ('users', 251),
        ('users', 500),
        ('users', 1000),
        ('users', 0),
        ('users', -1),
        ('users', -10),
        ('users', -25),
        ('tags', 251),
        ('tags', 500),
        ('tags', 1000),
        ('tags', 0),
        ('tags', -1),
        ('tags', -10),
        ('tags', -25),
        ('user_settings', 251),
        ('user_settings', 500),
        ('user_settings', 1000),
        ('user_settings', 0),
        ('user_settings', -1),
        ('user_settings', -10),
        ('user_settings', -25),
        ('api_clients', 251),
        ('api_clients', 500),
        ('api_clients', 1000),
        ('api_clients', 0),
        ('api_clients', -1),
        ('api_clients', -10),
        ('api_clients', -25),
        ('api_tokens', 251),
        ('api_tokens', 500),
        ('api_tokens', 1000),
        ('api_tokens', 0),
        ('api_tokens', -1),
        ('api_tokens', -10),
        ('api_tokens', -25),
    ),
)
def test_retrieval_short_lived_with_pagination_invalid_page_size(
    api_client: TestClient,
    endpoint: str,
    page_size: int,
) -> None:
    """Test that the retrieval endpoint works with a invalid page size.

    Unhappy path test; should result in a error 400

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        page_size: the page size.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'
    # Set the endpoint
    endpoint = create_endpoint_url(endpoint, {'page_size': page_size})

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )

    # Validate the answer
    assert result.status_code == 400


@pytest.mark.parametrize(
    'endpoint, page_size, page',
    (
        ('users', 10, 0),
        ('users', 10, 4),
        ('tags', 10, 0),
        ('tags', 10, 4),
        ('user_settings', 10, 0),
        ('user_settings', 10, 4),
        ('api_clients', 10, 0),
        ('api_clients', 10, 4),
        ('api_tokens', 10, 0),
        ('api_tokens', 10, 4),
    ),
)
def test_retrieval_short_lived_with_pagination_invalid_page(
    api_client: TestClient,
    endpoint: str,
    page_size: int,
    page: int,
) -> None:
    """Test that the retrieval endpoint works with a invalid page.

    Unhappy path test; should result in a error 400

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        page: the page.
        page_size: the page size.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'
    # Set the endpoint
    endpoint = create_endpoint_url(
        endpoint, {'page': page, 'page_size': page_size}
    )

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )

    # Validate the answer
    assert result.status_code == 400
