import copy
import typing as t

import jsonpath_ng  # type:ignore

from openapydantic import common
from openapydantic import versions

ComponentType = common.ComponentType
OpenApiVersion = common.OpenApiVersion
get_component_object_proxy = versions.get_component_object_proxy


def get_ref_data(
    *,
    ref: str,
) -> t.Tuple[ComponentType, str]:
    ref_type = None
    ref_key = None
    try:
        ref_split = ref.split("/")  # format #/components/schemas/Pet
        ref_type = ComponentType(ref_split[2])
        ref_key = ref_split[-1]
    except Exception as exc:
        raise ValueError("Invalid reference format") from exc
    return ref_type, ref_key


def validate_references_format(
    references: t.List[str],
) -> None:
    for ref in references:
        if ".yaml" in ref or ".json" in ref:
            raise NotImplementedError("File reference not implemented")
        if not ref.startswith("#/"):
            raise ValueError(f"reference {ref} has invalid format")


def find_ref(
    *,
    obj: t.Any,
) -> t.List[str]:
    jsonpath_expr = jsonpath_ng.parse(  # type:ignore
        "$..'$ref'",
    )
    return list(
        set([match.value for match in jsonpath_expr.find(obj)])  # type:ignore
    )


class ComponentsResolver:
    with_ref: t.Dict[str, t.Any] = {}
    without_ref: t.Dict[str, t.Any] = {}
    ref_find = False
    consolidate_count = 0
    self_ref: t.List[str] = []

    @classmethod
    def init(cls):
        cls.with_ref = {}
        cls.without_ref = {}
        cls.ref_find = False
        cls.consolidate_count = 0

        for elt in ComponentType:
            cls.with_ref[elt.name] = {}
            cls.without_ref[elt.name] = {}
            cls.self_ref = []

    @classmethod
    def _list_self_references(
        cls,
        *,
        key: str,
        component_type: ComponentType,
        references: t.List[str],
    ) -> None:
        for ref in references:

            ref_type, ref_key = get_ref_data(
                ref=ref,
            )

            if ref_type == component_type and ref_key == key:
                cls.self_ref.append(ref)

    @classmethod
    def _search_component_for_ref(
        cls,
        *,
        key: str,
        value: t.Dict[str, t.Any],
        component_type: ComponentType,
    ):
        references = find_ref(
            obj=value,
        )

        cls.ref_find = bool(references)

        validate_references_format(
            references=references,
        )

        cls._list_self_references(
            key=key,
            component_type=component_type,
            references=references,
        )

        if references:
            cls.with_ref[component_type.name][key] = {}
            cls.with_ref[component_type.name][key]["values"] = value
            cls.with_ref[component_type.name][key]["references"] = references
        else:
            cls.without_ref[component_type.name][key] = value

    @classmethod
    def _search_components_for_ref(
        cls,
        *,
        components: t.Dict[str, t.Any],
        component_type: ComponentType,
    ):
        for key, value in components.items():
            cls._search_component_for_ref(
                key=key,
                value=value,
                component_type=component_type,
            )

    @staticmethod
    def _get_component_object(
        component_type: ComponentType,
        values: t.Dict[str, t.Any],
        version: OpenApiVersion,
    ) -> t.Dict[str, t.Any]:
        if version == OpenApiVersion.v3_0_2:
            return get_component_object_proxy(
                component_type=component_type,
                values=values,
                version=version,
            )
        raise NotImplementedError()

    @classmethod
    def _check_references_availables(
        cls,
        *,
        references: t.List[str],
        component_type: ComponentType,
        key: str,
    ) -> bool:

        for ref in references:
            ref_type, ref_key = get_ref_data(
                ref=ref,
            )

            if ref_type == component_type and key == ref_key:
                continue

            if not cls.without_ref[ref_type.name].get(ref_key):
                # print(f"ref unavailable: {ref}")
                return False
            # print(f"ref available: {ref}")
        return True

    @classmethod
    def _consolidate_components(
        cls,
        *,
        component_type: ComponentType,
        version: OpenApiVersion,
    ) -> None:
        cls.consolidate_count = cls.consolidate_count + 1
        component_dict = {}
        with_ref_copy = copy.deepcopy(cls.with_ref[component_type.name])

        for key, values in with_ref_copy.items():
            references = values["references"]

            # print(f"Trying to create {component_type.name}:{key}")
            # if not all references are availables
            if not cls._check_references_availables(
                references=references,
                key=key,
                component_type=component_type,
            ):
                # print(f"Not all references ready for:{component_type.name}:{key}")
                # print("next...")
                continue

            component_dict = cls._get_component_object(
                component_type=component_type,
                values=values["values"],
                version=version,
            )

            cls.without_ref[component_type.name][key] = component_dict
            del cls.with_ref[component_type.name][key]

        if len(cls.with_ref[component_type.name]):
            cls._consolidate_components(
                component_type=component_type,
                version=version,
            )

    @classmethod
    def resolve(
        cls,
        *,
        raw_api: t.Dict[str, t.Any],
        version: OpenApiVersion,
    ) -> None:
        cls.init()

        components = raw_api.get("components")
        if not components:
            # print("No components in this api")
            return

        for elt in ComponentType:
            component = components.get(elt.value)
            if component:
                cls._search_components_for_ref(
                    components=component,
                    component_type=elt,
                )

        for elt in ComponentType:
            component = components.get(elt.value)
            if component:
                cls._consolidate_components(
                    component_type=elt,
                    version=version,
                )
            # print(
            #     f"Recursive consolidate count for component {elt.name}:"
            #     f"{cls.consolidate_count}"
            # )
