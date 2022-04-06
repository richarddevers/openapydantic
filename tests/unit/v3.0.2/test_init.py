from pytest_mock import MockerFixture

from openapydantic import common
from openapydantic import resolver
from openapydantic import versions
from tests.unit import conftest

FixtureLoader = conftest.FixtureLoader
ComponentType = common.ComponentType
openapi_302 = versions.openapi_302


def test_load_api_ok(
    mocker: MockerFixture,
    fixture_loader: FixtureLoader,
) -> None:
    m_resolver = mocker.spy(
        resolver.ComponentsResolver,
        "resolve",
    )
    raw_api = fixture_loader.load_yaml("simple.yaml")

    openapi_302.load_api(
        raw_api=raw_api,
    )

    m_resolver.assert_called_once_with(
        raw_api=raw_api,
        version=common.OpenApiVersion.v3_0_2,
    )
