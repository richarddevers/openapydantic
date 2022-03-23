import typing as t

import yaml

from openapydantic import common as common
from openapydantic import openapi_302 as openapi_302

OpenApi = common.OpenApi
OpenApi302 = openapi_302.OpenApi302


async def load_spec(
    file_path: str,
    mode: t.Optional[str] = None,
) -> t.Dict[t.Any, t.Any]:
    if not mode:
        mode = "r"

    with open(file_path, "r") as file:
        result = yaml.safe_load(file)

    return result


async def parse_api(file_path: str) -> OpenApi:
    api = await load_spec(file_path=file_path)

    if not api:
        raise ValueError("Api specification looks empty")

    openapi_version = api.get("openapi")

    if not openapi_version:
        raise ValueError("openapi version not specified")

    if openapi_version == OpenApi302.version.value:
        return OpenApi302(**api)

    raise NotImplementedError(f"Unsupported openapi version:{openapi_version}")
