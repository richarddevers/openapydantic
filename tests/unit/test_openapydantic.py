import os

import pytest

import openapydantic


@pytest.mark.asyncio
async def test_parse_api_empty() -> None:
    file_path = os.path.join(os.path.dirname(__file__), "fixture", "api-empty.yaml")
    with pytest.raises(ValueError):
        await openapydantic.parse_api(file_path=file_path)


@pytest.mark.asyncio
async def test_parse_api_no_version() -> None:
    file_path = os.path.join(
        os.path.dirname(__file__), "fixture", "api-no-version.yaml"
    )
    with pytest.raises(ValueError):
        await openapydantic.parse_api(file_path=file_path)


@pytest.mark.asyncio
async def test_parse_api_raise_unsupported_version() -> None:
    file_path = os.path.join(
        os.path.dirname(__file__), "fixture", "api-unsupported-version.yaml"
    )
    with pytest.raises(NotImplementedError):
        await openapydantic.parse_api(file_path=file_path)
