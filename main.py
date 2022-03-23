import json

import yaml

import openapydantic

raw_api = None
with open("openapi-spec.json", "r") as file:
    raw_api = yaml.safe_load(file)


api = openapydantic.OpenApi302(**raw_api)

ser = json.loads(
    api.json(
        by_alias=True,
        exclude_defaults=True,
        exclude_none=True,
        exclude_unset=True,
    )
)
breakpoint()
with open("data.json", "w") as fp:
    fp.write(
        api.json(
            by_alias=True,
            exclude_defaults=True,
            exclude_none=True,
            exclude_unset=True,
        )
    )
