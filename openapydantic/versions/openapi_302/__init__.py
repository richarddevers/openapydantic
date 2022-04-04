# https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md

import typing as t

import pydantic

import openapydantic
from openapydantic.versions.openapi_302.models import Components
from openapydantic.versions.openapi_302.models import ExternalDocs
from openapydantic.versions.openapi_302.models import Info
from openapydantic.versions.openapi_302.models import Paths
from openapydantic.versions.openapi_302.models import SecurityRequirement
from openapydantic.versions.openapi_302.models import Server
from openapydantic.versions.openapi_302.models import Tag

Field = pydantic.Field

OpenApiVersion = openapydantic.common.OpenApiVersion
OpenApiBaseModel = openapydantic.common.OpenApiBaseModel


class OpenApi302(OpenApiBaseModel):
    __version__: t.ClassVar[OpenApiVersion] = OpenApiVersion.v3_0_2
    components: t.Optional[Components]
    openapi: OpenApiVersion
    info: Info
    paths: Paths
    tags: t.Optional[t.List[Tag]]
    servers: t.Optional[t.List[Server]]
    security: t.Optional[t.List[SecurityRequirement]]
    external_docs: t.Optional[ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )
    raw_api: t.Dict[str, t.Any]

    class Config:
        extra = "forbid"


def load_api(
    *,
    raw_api: t.Dict[str, t.Any],
) -> OpenApi302:
    openapydantic.common.ComponentsResolver.resolve(
        raw_api=raw_api,
        version=OpenApiVersion.v3_0_2,
    )
    data: t.Dict[str, t.Any] = {
        **raw_api,
        "raw_api": raw_api,
    }
    api = OpenApi302(**data)

    return api
