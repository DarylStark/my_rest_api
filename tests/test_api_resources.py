"""Tests for the resources/ endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    'endpoint, expected_count',
    (
        ('users', 3),
        ('tags', 3),
        ('user_settings', 3),
        ('api_clients', 1),
    ),
)
def test_retrieval_as_root_short_lived(
    api_client: TestClient,
    endpoint: str,
    expected_count: int,
) -> None:
    """Test that the retrieval endpoint works.

    Happy path test; should always be a success and return some data. We test
    retrieving data without any filters for all resources.

    Args:
        api_client: the test client.
        endpoint: the endpoint to test.
        expected_count: the expected count of items.
    """
    _token = 'Cbxfv44aNlWRMu4bVqawWu9vofhFWmED'
    # Set the endpoint
    endpoint = f'/resources/{endpoint}'

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response) == expected_count


@pytest.mark.parametrize(
    'endpoint, expected_count, flt',
    (
        ('users', 1, 'id==1'),
        ('users', 2, 'id!=1'),
        ('users', 1, 'id<2'),
        ('users', 2, 'id>1'),
        ('users', 2, 'id<=2'),
        ('users', 2, 'id>=2'),
        ('users', 1, 'username==root'),
        ('users', 1, 'username==root,id==1'),
        ('users', 0, 'username==root,id==2'),
        ('users', 1, 'username=contains=normal'),
        ('users', 1, 'username=contains=normal,email=contains=normal'),
        ('users', 2, 'username=!contains=service'),
        ('users', 1, 'fullname==root'),
        ('users', 1, 'fullname=contains=normal'),
        ('users', 2, 'fullname=!contains=service'),
        ('users', 1, 'email==normal_user@example.com'),
        ('users', 1, 'email=contains=normal_user'),
        ('users', 2, 'email=!contains=service'),
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
    ),
)
def test_retrieval_as_root_short_lived_with_valid_filters(
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
    args: dict[str, str] = {}
    if flt:
        args['filter'] = flt

    # Create the endpoint string
    args_string = ''
    if len(args):
        args_string = '&'.join(
            [f'{argument}={value}' for argument, value in args.items()]
        )
    endpoint = f'/resources/{endpoint}?{args_string}'

    # Do the request
    result = api_client.get(
        endpoint,
        headers={'X-API-Token': _token},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == 200
    assert len(response) == expected_count
