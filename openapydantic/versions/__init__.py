import typing as t

import yaml

from openapydantic import common
from openapydantic.versions import openapi_302

OpenApi = (
    openapi_302.OpenApi302
)  # will be a tuple when there'll be more than one version


async def load_spec(
    *,
    file_path: str,
    mode: t.Optional[str] = None,
) -> t.Dict[t.Any, t.Any]:
    if not mode:
        mode = "r"

    with open(file_path, "r") as file:
        result = yaml.safe_load(file)

    return result


async def load_api(
    *,
    file_path: str,
    version: t.Optional[common.OpenApiVersion] = None,
) -> OpenApi:
    raw_api = await load_spec(file_path=file_path)
    if not raw_api:
        raise ValueError("Api specification looks empty")

    spec_version = raw_api.get("openapi")

    if not spec_version:
        raise ValueError("openapi version not specified")

    if (
        version == common.OpenApiVersion.v3_0_2
        or spec_version == openapi_302.OpenApi302.__version__.value
    ):
        return openapi_302.load_api(raw_api=raw_api)

    raise NotImplementedError(f"Unsupported openapi version:{spec_version}")


def get_component_object_proxy(
    component_type: common.ComponentType,
    values: t.Dict[str, t.Any],
    version: common.OpenApiVersion,
) -> t.Dict[str, t.Any]:
    if version == common.OpenApiVersion.v3_0_2:
        return openapi_302.get_component_object(
            component_type=component_type,
            values=values,
        )
    raise NotImplementedError()
