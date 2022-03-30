import os

import pytest

import openapydantic


@pytest.mark.asyncio
async def test_load_api_empty() -> None:
    file_path = os.path.join(os.path.dirname(__file__), "fixture", "api-empty.yaml")
    with pytest.raises(ValueError):
        await openapydantic.load_api(file_path=file_path)


@pytest.mark.asyncio
async def test_load_api_no_version() -> None:
    file_path = os.path.join(
        os.path.dirname(__file__), "fixture", "api-no-version.yaml"
    )
    with pytest.raises(ValueError):
        await openapydantic.load_api(file_path=file_path)


@pytest.mark.asyncio
async def test_load_api_raise_unsupported_version() -> None:
    file_path = os.path.join(
        os.path.dirname(__file__), "fixture", "api-unsupported-version.yaml"
    )
    with pytest.raises(NotImplementedError):
        await openapydantic.load_api(file_path=file_path)
