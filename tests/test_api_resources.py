"""Tests for the resources/ endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    'endpoint, expected_code, expected_count, flt',
    (
        ('users', 200, 3, None),
        ('users', 200, 1, 'id==1'),
        ('users', 200, 2, 'id!=1'),
        ('users', 200, 1, 'id<2'),
        ('users', 200, 2, 'id>1'),
        ('users', 200, 2, 'id<=2'),
        ('users', 200, 2, 'id>=2'),
        ('users', 200, 1, 'username==root'),
        ('users', 200, 1, 'username=contains=normal'),
        ('users', 200, 2, 'username=!contains=service'),
        ('users', 200, 1, 'fullname==root'),
        ('users', 200, 1, 'fullname=contains=normal'),
        ('users', 200, 2, 'fullname=!contains=service'),
        ('users', 200, 1, 'email==normal_user@example.com'),
        ('users', 200, 1, 'email=contains=normal_user'),
        ('users', 200, 2, 'email=!contains=service'),
        ('tags', 200, 3, None),
        ('tags', 200, 1, 'id==1'),
        ('tags', 200, 2, 'id!=1'),
        ('tags', 200, 2, 'id<3'),
        ('tags', 200, 2, 'id>1'),
        ('tags', 200, 3, 'id<=3'),
        ('tags', 200, 2, 'id>=2'),
        ('tags', 200, 1, 'title==root_tag_1'),
        ('tags', 200, 1, 'title=contains=tag_1'),
        ('tags', 200, 2, 'title=!contains=tag_1'),
        ('user_settings', 200, 3, None),
        ('user_settings', 200, 1, 'id==1'),
        ('user_settings', 200, 2, 'id!=1'),
        ('user_settings', 200, 2, 'id>1'),
        ('user_settings', 200, 2, 'id<3'),
        ('user_settings', 200, 2, 'id>=2'),
        ('user_settings', 200, 2, 'id<=2'),
        ('user_settings', 200, 1, 'setting==root_test_setting_1'),
        ('user_settings', 200, 3, 'setting=contains=root_test_setting'),
        ('user_settings', 200, 2, 'setting=!contains=_1'),
        ('user_settings', 200, 1, 'value==test_value_1'),
        ('user_settings', 200, 3, 'value=contains=test_value'),
        ('user_settings', 200, 2, 'value=!contains=_1'),
        ('api_clients', 200, 1, None),
        ('api_clients', 200, 1, 'id==1'),
        ('api_clients', 200, 0, 'id!=1'),
        ('api_clients', 200, 0, 'id>1'),
        ('api_clients', 200, 1, 'id<3'),
        ('api_clients', 200, 0, 'id>=2'),
        ('api_clients', 200, 1, 'id<=2'),
        ('api_clients', 200, 1, 'app_name==root_api_client_1'),
        ('api_clients', 200, 1, 'app_name=contains=api_client'),
        ('api_clients', 200, 0, 'app_name=!contains=api_client'),
        ('api_clients', 200, 1, 'app_publisher==root_api_client_1_publisher'),
        ('api_clients', 200, 1, 'app_publisher=contains=publisher'),
        ('api_clients', 200, 0, 'app_publisher=!contains=publisher'),
    ),
)
def test_retrieval_as_root_short_lived(
    api_client: TestClient,
    endpoint: str,
    expected_code: int,
    expected_count: int,
    flt: str | None,
) -> None:
    """Test that the retrieval endpoint works.

    Happy path test; should always be a success and return some data. We test
    all the possible filters for the retrieval endpoint for all the possible
    resources.

    Args:
        api_client: the test client.
        random_api_token_root: the random API token.
        endpoint: the endpoint to test.
        expected_code: the expected status code.
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
    assert result.status_code == expected_code
    assert len(response) == expected_count
