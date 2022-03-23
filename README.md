# Openapydantic

[openapi](https://github.com/OAI/OpenAPI-Specification) specification validator based on [pydantic](https://pydantic-docs.helpmanual.io/).

## Openapi versions supported

- ❌ 2.0
- ❌ 3.0.0
- ❌ 3.0.1
- ✅ 3.0.2
- ❌ 3.0.3
- ❌ 3.1.0

In my understanding, openapi versions are retrocompatibles (except for major version).

So 3.0.2 specification should be able to handle 3.0.0 and 3.0.1 data.

Unittests handle this case (3.0.2 object automatically try to load previous version fixtures).

## Installation

Depending on your preference...

```
    pip install openapydantic
```

...or...

```
    poetry add openapydantic
```

## Usage

Openapydantic provide an openapi specification (a.k.a "swagger file" in version 2.X) parser based on pydantic.

This object represent an openapi structure for a specific openapi version.

The object's version is based on the openapi specification version.

Using parser:

```python
import asyncio

import openapydantic

api = asyncio.run(openapydantic.parse_api(file_path="openapi-spec.yaml"))
print(api.info)
# if my openapi version is "3.0.2", api is an instance of OpenApi302
```

You can use an explicit openapi version but you have to pass a dict object.

It may be useful for backward compatibility (for eg: create an OpenApi302 object using data from an 3.0.1 openapi specfication ).

```python
import yaml

import openapydantic

raw_api=None
with open("openapi-spec.yaml", "r") as file:
    raw_api = yaml.safe_load(file)

api = openapydantic.OpenApi302(**raw_api) # 3.0.2 openapi pydantic object
print(api.info)
```

For more usage example, please refers to the *tests/* folder
