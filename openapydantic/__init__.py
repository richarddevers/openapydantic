import typing as t

import yaml

from openapydantic import common as common
from openapydantic import openapi_302 as openapi_302

OpenApi = common.OpenApi
OpenApi302 = openapi_302.OpenApi302
load_api_302 = openapi_302.load_api


async def load_spec(
    file_path: str,
    mode: t.Optional[str] = None,
) -> t.Dict[t.Any, t.Any]:
    if not mode:
        mode = "r"

    with open(file_path, "r") as file:
        result = yaml.safe_load(file)

    return result


async def load_api(file_path: str) -> OpenApi:
    raw_api = await load_spec(file_path=file_path)
    if not raw_api:
        raise ValueError("Api specification looks empty")

    openapi_version = raw_api.get("openapi")

    if not openapi_version:
        raise ValueError("openapi version not specified")

    if openapi_version == OpenApi302.__version__.value:
        return load_api_302(raw_api=raw_api)

    raise NotImplementedError(f"Unsupported openapi version:{openapi_version}")
