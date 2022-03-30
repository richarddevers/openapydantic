import pytest

import openapydantic
from tests.unit import conftest

list_specific_fixtures_version = conftest.list_specific_fixtures_version
SpecVersion = conftest.SpecVersion
FixtureLoader = conftest.FixtureLoader
FixturesVersion = conftest.FixturesVersion

OpenApi302 = openapydantic.OpenApi302
ComponentsParser = openapydantic.openapi_302.ComponentsParser

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
    openapydantic.OpenApi302(**raw_api)


@pytest.mark.parametrize("file_path", retro_fixture.ko)
@pytest.mark.asyncio
async def test_parse_retro_api_ko(
    file_path: str,
) -> None:
    with pytest.raises(Exception):
        raw_api = await openapydantic.load_spec(file_path)
        openapydantic.OpenApi302(**raw_api)


@pytest.mark.parametrize("file_path", fixtures_v3_0_2.ok)
@pytest.mark.asyncio
async def test_load_api_ok(
    file_path: str,
) -> None:
    raw_api = await openapydantic.load_spec(file_path)
    openapydantic.OpenApi302(**raw_api)


@pytest.mark.parametrize("file_path", fixtures_v3_0_2.ko)
@pytest.mark.asyncio
async def test_parse_api_ko(
    file_path: str,
) -> None:
    with pytest.raises(Exception):
        raw_api = await openapydantic.load_spec(file_path)
        openapydantic.OpenApi302(**raw_api)


@pytest.mark.asyncio
async def test_parse_api_ref_unmanaged_file_format(
    fixture_loader: FixtureLoader,
) -> None:
    with pytest.raises(Exception):
        raw_api = fixture_loader.load_yaml("ref-error-unmanaged-file-format.yaml")
        openapydantic.OpenApi302(**raw_api)


@pytest.mark.asyncio
async def test_parse_api_ref_invalid_path_format(
    fixture_loader: FixtureLoader,
) -> None:
    with pytest.raises(Exception):
        raw_api = fixture_loader.load_yaml("ref-error-invalid-path-format.yaml")
        openapydantic.OpenApi302(**raw_api)


@pytest.mark.asyncio
async def test_components_interpolation_1(
    fixture_loader: FixtureLoader,
) -> None:
    raw_api = fixture_loader.load_yaml(filename="components_1.yaml")
    expected = fixture_loader.load_json(filename="components_1.json")

    api = openapydantic.OpenApi302(**raw_api)

    assert expected == api.as_clean_dict()


@pytest.mark.asyncio
async def test_components_interpolation_2(
    fixture_loader: FixtureLoader,
) -> None:
    raw_api = fixture_loader.load_yaml(filename="components_2.yaml")
    expected = fixture_loader.load_json(filename="components_2.json")

    api = openapydantic.OpenApi302(**raw_api)

    assert expected == api.as_clean_dict()


@pytest.mark.asyncio
async def test_components_interpolation_3(
    fixture_loader: FixtureLoader,
) -> None:
    raw_api = fixture_loader.load_yaml(filename="components_3.yaml")
    expected = fixture_loader.load_json(filename="components_3.json")

    api = openapydantic.OpenApi302(**raw_api)

    assert expected == api.as_clean_dict()


@pytest.mark.asyncio
async def test_components_interpolation_4(
    fixture_loader: FixtureLoader,
) -> None:
    raw_api = fixture_loader.load_yaml(filename="components_4.yaml")
    expected = fixture_loader.load_json(filename="components_4.json")

    api = openapydantic.OpenApi302(**raw_api)

    assert expected == api.as_clean_dict()
