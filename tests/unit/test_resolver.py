import typing as t

import jsonpath_ng
import pytest
from pytest_mock import MockerFixture

from openapydantic import common
from openapydantic import resolver

ComponentType = common.ComponentType
ComponentsResolver = resolver.ComponentsResolver


def test_get_ref_data_ok() -> None:
    ref = "#/components/schemas/Pet"

    ref_type, ref_key = resolver.get_ref_data(
        ref=ref,
    )

    assert ref_type == ComponentType.schemas
    assert ref_key == "Pet"


def test_get_ref_data_ko() -> None:
    ref = "invalid-ref"

    with pytest.raises(ValueError):
        resolver.get_ref_data(
            ref=ref,
        )


def test_validate_references_format_ko_json() -> None:
    references = ["#/Pet.json"]

    with pytest.raises(NotImplementedError):
        resolver.validate_references_format(
            references=references,
        )


def test_validate_references_format_ko_yaml() -> None:
    references = ["#/Pet.yaml"]

    with pytest.raises(NotImplementedError):
        resolver.validate_references_format(
            references=references,
        )


def test_validate_references_format_ko_format() -> None:
    references = ["schemas/Pet/"]

    with pytest.raises(ValueError):
        resolver.validate_references_format(
            references=references,
        )


def test_find_ref(
    mocker: MockerFixture,
) -> None:
    obj = {
        "ref1": {"$ref": "#/ref-1"},
        "ref2": {"$ref": "#/ref-2"},
        "ref3": {"$ref": "#/ref-2"},
    }
    m_parse = mocker.spy(
        jsonpath_ng,
        "parse",
    )

    references = resolver.find_ref(
        obj=obj,
    )

    m_parse.assert_called_once_with("$..'$ref'")
    assert references.sort() == ["#/ref-1", "#/ref-2"].sort()


def test_components_resolver_init() -> None:
    data: t.Dict[str, t.Any] = {
        "schemas": {},
        "headers": {},
        "responses": {},
        "parameters": {},
        "examples": {},
        "request_bodies": {},
        "links": {},
        "callbacks": {},
    }
    ComponentsResolver.with_ref = {}
    ComponentsResolver.without_ref = {}
    ComponentsResolver.ref_find = True
    ComponentsResolver.consolidate_count = 10
    ComponentsResolver.self_ref = ["#/components/schemas/Pet"]

    ComponentsResolver.init()

    assert ComponentsResolver.with_ref == data
    assert ComponentsResolver.without_ref == data
    assert not ComponentsResolver.ref_find
    assert not ComponentsResolver.consolidate_count
    assert not ComponentsResolver.self_ref


def test_components_resolver_list_self_reference_ok() -> None:
    key = "Pet"
    component_type = ComponentType.schemas
    references = ["#/components/schemas/Pet"]

    ComponentsResolver._list_self_references(
        key=key,
        component_type=component_type,
        references=references,
    )

    assert ComponentsResolver.self_ref == references
    ComponentsResolver.init()


def test_components_resolver_list_self_reference_ok_no_ref() -> None:
    key = "Pet"
    component_type = ComponentType.schemas
    references = ["#/components/schemas/Hola"]

    ComponentsResolver._list_self_references(
        key=key,
        component_type=component_type,
        references=references,
    )

    assert ComponentsResolver.self_ref == []
