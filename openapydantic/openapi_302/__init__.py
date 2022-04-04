# https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md

import typing as t

import pydantic

from openapydantic import common
from openapydantic.openapi_302.models import Components
from openapydantic.openapi_302.models import ComponentsResolver
from openapydantic.openapi_302.models import ExternalDocs
from openapydantic.openapi_302.models import Info
from openapydantic.openapi_302.models import Paths
from openapydantic.openapi_302.models import SecurityRequirement
from openapydantic.openapi_302.models import Server
from openapydantic.openapi_302.models import Tag

Field = pydantic.Field

OpenApiVersion = common.OpenApiVersion
OpenApiBaseModel = common.OpenApiBaseModel


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
    ComponentsResolver.resolve(raw_api=raw_api)
    data: t.Dict[str, t.Any] = {
        **raw_api,
        "raw_api": raw_api,
    }
    api = OpenApi302(**data)

    return api
