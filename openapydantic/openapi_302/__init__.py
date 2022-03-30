# https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md

import typing as t

import pydantic

from openapydantic import common
from openapydantic.openapi_302 import models

Field = pydantic.Field

OpenApiVersion = common.OpenApiVersion


class OpenApi302(pydantic.BaseModel):
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
