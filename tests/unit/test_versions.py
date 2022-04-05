import builtins
import os
import typing as t

import pytest
import yaml
from pytest_mock import MockerFixture

from openapydantic import common
from openapydantic import versions


@pytest.fixture
def raw_api() -> t.Dict[str, t.Any]:
    return {
        "openapi": "3.0.2",
        "info": {
            "version": "1.0.0",
            "title": "Swagger Petstore",
            "contact": {"email": "apiteam@swagger.io"},
        },
        "paths": {
            "/pet": {
                "get": {
                    "tags": ["user"],
                    "summary": "Get user",
                    "responses": {
                        "200": {
                            "description": "successful operation",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Pet"}
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "id": {"type": "integer", "format": "int64"},
                        "name": {"type": "string", "example": "doggie"},
                        "status": {
                            "type": "string",
                            "description": "pet status in the store",
                            "enum": ["available", "pending", "sold"],
                        },
                    },
                }
            }
        },
    }


@pytest.mark.asyncio
async def test_load_spec_ok(
    mocker: MockerFixture,
) -> None:
    m_open = mocker.spy(builtins, "open")
    m_yaml = mocker.spy(yaml, "safe_load")
    file_name = "simple.yaml"
    file_path = os.path.join(os.path.dirname(__file__), "fixture", file_name)

    result = await versions.load_spec(file_path=file_path)

    m_open.assert_called_once_with(file_path, "r")
    m_yaml.assert_called_once_with(m_open.spy_return)


@pytest.mark.asyncio
async def test_load_api_ok(
    raw_api: t.Dict[str, t.Any],
    mocker: MockerFixture,
) -> None:
    m_load_spec = mocker.patch.object(
        versions,
        "load_spec",
        return_value=raw_api,
    )
    m_load_api_302 = mocker.patch.object(
        versions.openapi_302,
        "load_api",
    )

    result = await versions.load_api(
        file_path="fake",
        version=common.OpenApiVersion.v3_0_2,
    )

    m_load_spec.assert_called_once_with(
        file_path="fake",
    )
    m_load_api_302.assert_called_once_with(
        raw_api=m_load_spec.return_value,
    )


@pytest.mark.asyncio
async def test_get_component_object_proxy_ok(
    mocker: MockerFixture,
    raw_api: t.Dict[str, t.Any],
) -> None:
    m_load_api_302 = mocker.patch.object(
        versions.openapi_302,
        "get_component_object",
    )

    versions.get_component_object_proxy(
        component_type=common.ComponentType.schemas,
        values=raw_api,
        version=common.OpenApiVersion.v3_0_2,
    )

    m_load_api_302.assert_called_once_with(
        component_type=common.ComponentType.schemas,
        values=raw_api,
    )
