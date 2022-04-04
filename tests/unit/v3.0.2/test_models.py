import typing as t

import openapydantic

ComponentsResolver = openapydantic.common.ComponentsResolver


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
