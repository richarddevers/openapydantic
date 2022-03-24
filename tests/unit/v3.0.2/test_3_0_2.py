import pytest

import openapydantic
from tests.unit.conftest import FixtureLoader
from tests.unit.conftest import FixturesVersion
from tests.unit.conftest import SpecVersion
from tests.unit.conftest import list_specific_fixtures_version

OpenApi302 = openapydantic.OpenApi302

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
    # assert raw_api == json.loads(
    #     api.json(
    #         by_alias=True,
    #         exclude_defaults=True,
    #         exclude_none=True,
    #         exclude_unset=True,
    #     )
    # )


@pytest.mark.parametrize("file_path", fixtures_v3_0_2.ko)
@pytest.mark.asyncio
async def test_parse_api_ko(
    file_path: str,
) -> None:
    with pytest.raises(Exception):
        raw_api = await openapydantic.load_spec(file_path)
        openapydantic.OpenApi302(**raw_api)


@pytest.mark.asyncio
async def test_parse_api_valid_spec_extension(
    fixture_loader: FixtureLoader,
) -> None:
    raw_api = fixture_loader.load_yaml("x-extended.yaml")

    openapydantic.OpenApi302(**raw_api)


@pytest.mark.asyncio
async def test_parse_api_invalid_spec_extended(
    fixture_loader: FixtureLoader,
) -> None:
    with pytest.raises(Exception):
        raw_api = fixture_loader.load_yaml("y-extended.yaml")
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


# @pytest.mark.asyncio
# async def test_parse_api_oneshot() -> None:
#     raw_api = await openapydantic.load_spec(
#         "/workspaces/api/tests/unit/v3.0.2/fixture/ok/healthfit.yaml"
#     )
#     openapydantic.OpenApi302(**raw_api)
