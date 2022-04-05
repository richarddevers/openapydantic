# https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md

import typing as t

import pydantic

from openapydantic import common
from openapydantic import resolver
from openapydantic.versions.openapi_302 import models

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
) -> OpenApi302:
    resolver.ComponentsResolver.resolve(
        raw_api=raw_api,
        version=OpenApiVersion.v3_0_2,
    )
    data: t.Dict[str, t.Any] = {
        **raw_api,
        "raw_api": raw_api,
    }
    api = OpenApi302(**data)

    return api


def get_component_object(
    component_type: common.ComponentType,
    values: t.Dict[str, t.Any],
) -> t.Dict[str, t.Any]:
    if component_type == common.ComponentType.schemas:
        component = models.Schema(**values)
    elif component_type == common.ComponentType.headers:
        component = models.Header(**values)
    elif component_type == common.ComponentType.responses:
        component = models.Response(**values)
    elif component_type == common.ComponentType.parameters:
        component = models.Parameter(**values)
    elif component_type == common.ComponentType.examples:
        component = models.Example(**values)
    elif component_type == common.ComponentType.request_bodies:
        component = models.RequestBody(**values)
    elif component_type == common.ComponentType.links:
        component = models.Link(**values)
    elif component_type == common.ComponentType.callbacks:
        component = models.PathItem(**values)
    else:
        raise NotImplementedError()
    return component.as_clean_dict()
