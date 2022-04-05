import enum
import typing as t

import pydantic


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
