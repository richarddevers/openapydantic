import copy
import enum
import typing as t

import jsonpath_ng
import pydantic

from openapydantic import versions


class ComponentType(enum.Enum):
    schemas = "schemas"
    headers = "headers"
    responses = "responses"
    parameters = "parameters"
    examples = "examples"
    request_bodies = "requestBodies"
    links = "links"
    callbacks = "callbacks"


class OpenApiBaseModel(pydantic.BaseModel):
    def as_clean_json(
        self,
        *,
        exclude_components: bool = True,
        exclude_raw_api: bool = True,
    ) -> str:
        exclude: t.Set[str] = set()

        if exclude_components:
            exclude.add("components")

        if exclude_raw_api:
            exclude.add("raw_api")

        return self.json(
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
            exclude=exclude,
        )

    def as_clean_dict(
        self,
        *,
        exclude_components: bool = True,
        exclude_raw_api: bool = True,
    ) -> t.Dict[str, t.Any]:
        exclude: t.Set[str] = set()

        if exclude_components:
            exclude.add("components")

        if exclude_raw_api:
            exclude.add("raw_api")

        return self.dict(
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
            exclude=exclude,
        )


# could be:
# -------
# import http
# HTTPStatusCode = t.Literal[tuple(str(x.value) for x in http.HTTPStatus)]
# HTTPStatusCode.append("default")
# -------
# but typing won't works with that so \o/
HTTPStatusCode = t.Literal[
    "default",  # openapi spec add
    "100",
    "101",
    "102",
    "200",
    "201",
    "202",
    "203",
    "204",
    "205",
    "206",
    "207",
    "208",
    "226",
    "300",
    "301",
    "302",
    "303",
    "304",
    "305",
    "307",
    "308",
    "400",
    "401",
    "402",
    "403",
    "404",
    "405",
    "406",
    "407",
    "408",
    "409",
    "410",
    "411",
    "412",
    "413",
    "414",
    "415",
    "416",
    "417",
    "421",
    "422",
    "423",
    "424",
    "426",
    "428",
    "429",
    "431",
    "451",
    "500",
    "501",
    "502",
    "503",
    "504",
    "505",
    "506",
    "507",
    "508",
    "510",
    "511",
]


HTTPMethod = t.Literal[
    "get",
    "put",
    "post",
    "patch",
    "delete",
    "head",
    "options",
]

MediaType = t.Literal[
    "application/json",
    "application/xml",
    "application/octet-stream",
    "application/x-www-form-urlencoded",
    "application/json; charset=utf-8",
]


class OpenApiVersion(enum.Enum):
    v3_0_0 = "3.0.0"
    v3_0_1 = "3.0.1"
    v3_0_2 = "3.0.2"
    # v3_0_3 = "3.0.3"
    # v3_1_0 = "3.1.0"


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
    jsonpath_expr = jsonpath_ng.parse(
        "$..'$ref'",
    )  # type:ignore
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
            return versions.get_component_object_302(
                component_type=component_type,
                values=values,
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


def reference_interpolation(
    values: t.Dict[str, t.Any],
) -> t.Dict[str, t.Any]:
    ref = values.get("$ref")
    # print("====== VALIDATE ROOT ======")
    # print(f"ref:{ref}")
    if ref:
        # Avoir self reference here
        if ref in ComponentsResolver.self_ref:
            return values
        ref_type, ref_key = get_ref_data(
            ref=ref,
        )
        # print(f"ref_type:{ref_type.name}")
        # print(f"ref_key:{ref_key}")
        ref_found: t.Dict[str, t.Any] = ComponentsResolver.without_ref[
            ref_type.name
        ].get(ref_key)
        # print(f"ref_found:{ref_found}")
        if not ref_found:
            raise ValueError(f"Reference not found:{ref_type}/{ref_key}")

        return ref_found
    return values
