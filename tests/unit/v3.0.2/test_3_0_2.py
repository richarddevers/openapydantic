import json

import pytest

import openapydantic
from tests.unit import conftest

list_specific_fixtures_version = conftest.list_specific_fixtures_version
SpecVersion = conftest.SpecVersion
FixtureLoader = conftest.FixtureLoader
FixturesVersion = conftest.FixturesVersion

load_api = openapydantic.openapi_302.load_api

fixtures_v3_0_0 = list_specific_fixtures_version(version=SpecVersion.v3_0_0)
fixtures_v3_0_1 = list_specific_fixtures_version(version=SpecVersion.v3_0_1)
fixtures_v3_0_2 = list_specific_fixtures_version(version=SpecVersion.v3_0_2)

retro_fixture = FixturesVersion(
    ok=fixtures_v3_0_0.ok + fixtures_v3_0_1.ok,
    ko=fixtures_v3_0_0.ko + fixtures_v3_0_1.ko,
)


@pytest.mark.parametrize("file_path", retro_fixture.ok)
@pytest.mark.asyncio
async def test_parse_retro_api_ok(
    file_path: str,
) -> None:
    raw_api = await openapydantic.load_spec(file_path)
    load_api(raw_api=raw_api)


@pytest.mark.parametrize("file_path", retro_fixture.ko)
@pytest.mark.asyncio
async def test_parse_retro_api_ko(
    file_path: str,
) -> None:
    with pytest.raises(Exception):
        raw_api = await openapydantic.load_spec(file_path)
        load_api(raw_api=raw_api)


@pytest.mark.parametrize("file_path", fixtures_v3_0_2.ok)
@pytest.mark.asyncio
async def test_load_api_ok(
    file_path: str,
) -> None:
    raw_api = await openapydantic.load_spec(file_path)
    load_api(raw_api=raw_api)


@pytest.mark.parametrize("file_path", fixtures_v3_0_2.ko)
@pytest.mark.asyncio
async def test_parse_api_ko(
    file_path: str,
) -> None:
    with pytest.raises(Exception):
        raw_api = await openapydantic.load_spec(file_path)
        load_api(raw_api=raw_api)


@pytest.mark.asyncio
async def test_parse_api_ref_unmanaged_file_format(
    fixture_loader: FixtureLoader,
) -> None:
    with pytest.raises(Exception):
        raw_api = fixture_loader.load_yaml("ref-error-unmanaged-file-format.yaml")
        load_api(raw_api=raw_api)


@pytest.mark.asyncio
async def test_parse_api_ref_invalid_path_format(
    fixture_loader: FixtureLoader,
) -> None:
    with pytest.raises(Exception):
        raw_api = fixture_loader.load_yaml("ref-error-invalid-path-format.yaml")
        load_api(raw_api=raw_api)


@pytest.mark.parametrize(
    "api_index",
    [(1), (2), (3), (4)],
)
@pytest.mark.asyncio
async def test_reference_interpolation_x(
    fixture_loader: FixtureLoader, api_index: int
) -> None:
    raw_api = fixture_loader.load_yaml(filename=f"components_{api_index}.yaml")
    expected = fixture_loader.load_json(filename=f"components_{api_index}.json")

    api = load_api(raw_api=raw_api)

    assert expected == json.loads(api.as_clean_json())
