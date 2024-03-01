"""Tests for the resources/ endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    'endpoint, expected_code, expected_count, flt',
    (
        ('users', 200, 4, None),
        ('users', 200, 1, 'id==1'),
        ('users', 200, 3, 'id!=1'),
        ('users', 200, 3, 'id<4'),
        ('users', 200, 3, 'id>1'),
        ('users', 200, 3, 'id<=3'),
        ('users', 200, 3, 'id>=2'),
        ('users', 200, 1, 'username==root'),
        ('users', 200, 2, 'username=contains=normal'),
        ('users', 200, 3, 'username=!contains=service'),
        ('users', 200, 1, 'fullname==root'),
        ('users', 200, 2, 'fullname=contains=normal'),
        ('users', 200, 3, 'fullname=!contains=service'),
        ('users', 200, 1, 'email==normal_user_1@example.com'),
        ('users', 200, 2, 'email=contains=normal_user'),
        ('users', 200, 3, 'email=!contains=service'),
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
        ('api_clients', 200, 3, None),
    ),
)
def test_retrieval_as_root_short_lived(
    api_client: TestClient,
    random_api_token_root: str,
    endpoint: str,
    expected_code: int,
    expected_count: int,
    flt: str | None,
) -> None:
    """Test that the retrieval endpoint works.

    Args:
        api_client: the test client.
        random_api_token_root: the random API token.
        endpoint: the endpoint to test.
        expected_code: the expected status code.
        expected_count: the expected count of items.
        flt: the filter to use.
    """
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
        headers={'X-API-Token': random_api_token_root},
    )
    response = result.json()

    # Validate the answer
    assert result.status_code == expected_code
    assert len(response) == expected_count
