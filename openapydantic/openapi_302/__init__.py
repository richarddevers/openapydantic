# https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md

import typing as t

import pydantic

from openapydantic import common
from openapydantic.openapi_302 import models

Field = pydantic.Field

OpenApiVersion = common.OpenApiVersion
OpenApiBaseModel = common.OpenApiBaseModel


class OpenApi302(OpenApiBaseModel):
    __version__: t.ClassVar[OpenApiVersion] = OpenApiVersion.v3_0_2
    components: t.Optional[models.Components]
    openapi: OpenApiVersion
    info: models.Info
    paths: models.Paths
    tags: t.Optional[t.List[models.Tag]]
    servers: t.Optional[t.List[models.Server]]
    security: t.Optional[t.List[models.SecurityRequirement]]
    external_docs: t.Optional[models.ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )
    raw_api: t.Dict[str, t.Any]

    class Config:
        extra = "forbid"


def load_api(
    *,
    raw_api: t.Dict[str, t.Any],
    clean_memory: bool = True,
) -> OpenApi302:
    models.ComponentsResolver.resolve(raw_api=raw_api)

    data: t.Dict[str, t.Any] = {
        **raw_api,
        "raw_api": raw_api,
    }

    api = OpenApi302(**data)
    if clean_memory:
        models.ComponentsResolver.init()
    return api
