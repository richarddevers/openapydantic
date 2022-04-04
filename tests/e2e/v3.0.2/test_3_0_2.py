import json

import pytest

import openapydantic
from tests.e2e import conftest

list_specific_fixtures_version = conftest.list_specific_fixtures_version
SpecVersion = conftest.SpecVersion
FixtureLoader = conftest.FixtureLoader
FixturesVersion = conftest.FixturesVersion
OpenApiVersion = openapydantic.OpenApiVersion

load_api = openapydantic.load_api
load_api_302 = openapydantic.openapi_302.load_api

fixtures_v3_0_0 = list_specific_fixtures_version(version=SpecVersion.v3_0_0)
fixtures_v3_0_1 = list_specific_fixtures_version(version=SpecVersion.v3_0_1)
fixtures_v3_0_2 = list_specific_fixtures_version(version=SpecVersion.v3_0_2)

retro_fixture = FixturesVersion(
    ok=fixtures_v3_0_0.ok + fixtures_v3_0_1.ok,
    ko=fixtures_v3_0_0.ko + fixtures_v3_0_1.ko,
)


@pytest.mark.parametrize("file_path", retro_fixture.ok)
@pytest.mark.asyncio
async def test_retrocompatibility_ok(
    file_path: str,
) -> None:
    await load_api(
        file_path=file_path,
        version=OpenApiVersion.v3_0_2,
    )


@pytest.mark.parametrize("file_path", retro_fixture.ko)
@pytest.mark.asyncio
async def test_retrocompatibility_ko(
    file_path: str,
) -> None:
    with pytest.raises(Exception):
        await load_api(
            file_path=file_path,
            version=OpenApiVersion.v3_0_2,
        )


@pytest.mark.parametrize("file_path", fixtures_v3_0_2.ok)
@pytest.mark.asyncio
async def test_load_api_ok(
    file_path: str,
) -> None:
    await load_api(file_path=file_path)


@pytest.mark.parametrize("file_path", fixtures_v3_0_2.ko)
@pytest.mark.asyncio
async def test_parse_api_ko(
    file_path: str,
) -> None:
    with pytest.raises(Exception):
        await load_api(file_path=file_path)


@pytest.mark.asyncio
async def test_parse_api_ref_unmanaged_file_format(
    fixture_loader: FixtureLoader,
) -> None:
    with pytest.raises(Exception):
        raw_api = fixture_loader.load_yaml("ref-error-unmanaged-file-format.yaml")
        load_api_302(raw_api=raw_api)


@pytest.mark.asyncio
async def test_parse_api_ref_invalid_path_format(
    fixture_loader: FixtureLoader,
) -> None:
    with pytest.raises(Exception):
        raw_api = fixture_loader.load_yaml("ref-error-invalid-path-format.yaml")
        load_api_302(raw_api=raw_api)


@pytest.mark.asyncio
async def test_parse_api_self_reference(
    fixture_loader: FixtureLoader,
) -> None:
    expected = fixture_loader.load_json(filename="self-reference.json")
    raw_api = fixture_loader.load_yaml(filename="self-reference.yaml")

    api = load_api_302(raw_api=raw_api)

    assert expected == json.loads(api.as_clean_json())


@pytest.mark.parametrize(
    "api_index",
    [(1), (2), (3), (4)],
)
@pytest.mark.asyncio
async def test_reference_interpolation_x(
    fixture_loader: FixtureLoader,
    api_index: int,
) -> None:
    raw_api = fixture_loader.load_yaml(filename=f"components_{api_index}.yaml")
    expected = fixture_loader.load_json(filename=f"components_{api_index}.json")

    api = load_api_302(raw_api=raw_api)

    assert expected == json.loads(api.as_clean_json())


# @pytest.mark.asyncio
# async def test_reference_interpolation_x_index(fixture_loader: FixtureLoader) -> None:
#     raw_api = fixture_loader.load_yaml(filename="components_4.yaml")
#     expected = fixture_loader.load_json(filename="components_4.json")

#     api = load_api_302(raw_api=raw_api)
#     assert expected == json.loads(api.as_clean_json())


# @pytest.mark.asyncio
# async def test_oneshot() -> None:
#     file_path = (
#         "/workspaces/openapydantic/tests/e2e/v3.0.1/fixture/ok/self-reference.yaml"
#     )
#     raw_api = await openapydantic.load_spec(file_path=file_path)
#     api = load_api_302(raw_api=raw_api)
#     print(api.as_clean_json())


# @pytest.mark.asyncio
# async def test_oneshot(
#     fixture_loader: FixtureLoader,
# ) -> None:
#     raw_api = fixture_loader.load_yaml(filename=f"components_4.yaml")
#     load_api_302(raw_api=raw_api)
