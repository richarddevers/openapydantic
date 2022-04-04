from pytest_mock import MockerFixture

import openapydantic
from tests.unit import conftest

FixtureLoader = conftest.FixtureLoader
ComponentType = openapydantic.common.ComponentType
openapi_302 = openapydantic.openapi_302


def test_load_api_ok(
    mocker: MockerFixture,
    fixture_loader: FixtureLoader,
) -> None:
    m_resolver = mocker.spy(
        openapi_302.ComponentsResolver,
        "resolve",
    )
    raw_api = fixture_loader.load_yaml("simple.yaml")

    openapi_302.load_api(
        raw_api=raw_api,
    )

    m_resolver.assert_called_once_with(
        raw_api=raw_api,
    )
