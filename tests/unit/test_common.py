import typing as t

from openapydantic import common

OpenApiBaseModel = common.OpenApiBaseModel


class FakeClass(OpenApiBaseModel):
    attr1: str
    components: t.Dict[str, t.Any]
    raw_api: t.Dict[str, t.Any]


def test_as_clean_json_default() -> None:
    obj = FakeClass(
        attr1="ohla",
        components={"ohla": "ohalala"},
        raw_api={"ohla": "ohalalalal"},
    )

    result = obj.as_clean_json()

    assert result == '{"attr1": "ohla"}'


def test_as_clean_dict_default() -> None:
    obj = FakeClass(
        attr1="ohla",
        components={"ohla": "ohalala"},
        raw_api={"ohla": "ohalalalal"},
    )

    result = obj.as_clean_dict()

    assert result == {"attr1": "ohla"}
    assert not result.get("components")
    assert not result.get("raw_api")
