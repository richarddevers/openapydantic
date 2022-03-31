# Openapydantic

[openapi](https://github.com/OAI/OpenAPI-Specification) specification validator based on [pydantic](https://pydantic-docs.helpmanual.io/).

## Python version support

\>=3.8

## Openapi versions support

- ❌ 2.0
- 🟠 3.0.0
- 🟠 3.0.1
- ✅ 3.0.2
- ❌ 3.0.3
- ❌ 3.1.0

Openapi versions are retrocompatibles (except for major version).

So 3.0.2 specification should be able to handle 3.0.0 and 3.0.1 data.

Unit tests handle this case (3.0.2 object automatically try to load previous version fixtures).

## Installation

Depending on your preference...

```
    pip install openapydantic
```

...or...

```
    poetry add openapydantic
```

## Basic usage

### Api loader

Openapydantic provide an openapi specification (a.k.a "swagger file" in version 2.X) loader.

This loader returns a pydantic model so you can work with your specification like a common pydantic python object.

For each openapi specification version, a dedicated python class exist.

The loader can either automatically determine the class to provide...

```python
import asyncio

import openapydantic

api = asyncio.run(
    openapydantic.load_api(
        file_path="openapi-spec.yaml",
    ),
)
print(api.info)
# if my openapi version is "3.0.2", 'api' is an instance of OpenApi302
# if the version is not implemented, it will crash
```

... or you can also specify a specific version.

It may be useful for backward compatibility (for eg: create an OpenApi302 object using data from an 3.0.1 openapi specfication ).

```python
import asyncio

import openapydantic

OpenApiVersion = openapydantic.OpenApiVersion

api = asyncio.run(
    openapydantic.load_api(
        file_path="openapi-spec-3-0-1.yaml",
        version=OpenApiVersion.v3_0_2
    ),
)
# Here ,'api' is an OpenApi302 object, event if you send an 3.0.1 spec.

print(api.openapi)
>> 3.0.1 # version in the spec file
print(api.__version__)
>> 3.0.2 # openapi version supported for the object class
```

### Reference interpolation

Openapydantic will interpolate openapi references.

If your api looks like this:

```yaml
# my-api.yaml
openapi: 3.0.2
info:
  version: "1.0.0"
  title: Example
paths:
  /user:
    get:
      summary: Get user
      responses:
        "200":
          description: successful operation
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
          format: int64
        name:
          type: string
          example: "John Doe"
```

Once loaded, it will be usable like if it was ...

```yaml
openapi: 3.0.2
info:
  version: "1.0.0"
  title: Example
paths:
  /user:
    get:
      summary: Get user
      responses:
        "200":
          description: successful operation
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: integer
                    format: int64
                  name:
                    type: string
                    example: "John Doe"

```

And so you will be able to do things like...

```python
import asyncio

import openapydantic

api = asyncio.run(
    openapydantic.load_api(
        file_path="my-api.yaml",
    ),
)
print(api.info)
print(
    api.paths["/user"]
    .get.responses["200"]
    .content["application/json"]
    .schema_.properties["name"]
    .example
)
>> John Doe
```

As describe in the openapi specification some attributes are fix ('paths', 'content' etc...) and some can be mapping with a free key.

Mapping must be accessed like common dict, either by direct key loading, either using .get('*key*')

Note that file reference (e.g: "#/file.yaml" are currently not supported)

### Attributes name collision

Openapi specify some attribute which name are already reserved either by pydantic,either by the python language itself.

To access these attributes, you must use the Openapydantic specific name

| Attribute name | Openapydantic specific name |
|----------------|------------------------------|
| schema         | schema_                      |
| in             | in_                          |
| not            | not_                         |

e.g:

```python
print(
    api.paths["/user"]
    .get.responses["200"]
    .content["application/json"]
    .schema_
)
```

### Model export

You can access the original api you provided as a dict using the **raw_api** attribute.

```python
import asyncio

import openapydantic

api = asyncio.run(
    openapydantic.load_api(
        file_path="my-api.yaml",
    ),
)

print(api.raw_api)
>> {'openapi': '3.0.2', 'info': {'version': '1.0.0', 'title': 'Example'}, 'paths': {'/user': {'get': {'summary': 'Get user', 'responses': {'200': {'description': 'successful operation', 'content': {'application/json': {'schema': {'$ref': '#/components/schemas/User'}}}}}}}}, 'components': {'schemas': {'User': {'type': 'object', 'properties': {'id': {'type': 'integer', 'format': 'int64'}, 'name': {'type': 'string', 'example': 'John Doe'}}}}}}
```

You can export your data as json string or as python dict using specific methods:

```python
import asyncio

import openapydantic

api = asyncio.run(
    openapydantic.load_api(
        file_path="my-api.yaml",
    ),
)

print(api.as_clean_json())
>> {"openapi": "3.0.2", "info": {"title": "Example", "version": "1.0.0"}, "paths": {"/user": {"get": {"summary": "Get user", "responses": {"200": {"description": "successful operation", "content": {"application/json": {"schema": {"type": "object", "properties": {"id": {"type": "integer", "format": "int64"}, "name": {"type": "string", "example": "John Doe"}}}}}}}}}}}


print(api.as_clean_dict())
> {'openapi': <OpenApiVersion.v3_0_2: '3.0.2'>, 'info': {'title': 'Example', 'version': '1.0.0'}, 'paths': {'/user': {'get': {'summary': 'Get user', 'responses': {'200': {'description': 'successful operation', 'content': {'application/json': {'schema': {'type': <JsonType.object_: 'object'>, 'properties': {'id': {'type': <JsonType.integer: 'integer'>, 'format': 'int64'}, 'name': {'type': <JsonType.string: 'string'>, 'example': 'John Doe'}}}}}}}}}}}
```

Note that these functions are just wrapper to .dict() and .json() pydantic model with specific parameters.

By default, since the references are interpolated, the **components** root key is exclude.

If you want to have it in the output, you can set the **exclude_components** parameter to False.

```python
import asyncio

import openapydantic

api = asyncio.run(
    openapydantic.load_api(
        file_path="my-api.yaml",
    ),
)

print(
    api.as_clean_json(
        exclude_components=False,
    ),
)

>> {"components": {"schemas": {"User": {"type": "object", "properties": {"id": {"type": "integer", "format": "int64"}, "name": {"type": "string", "example": "John Doe"}}}}}, "openapi": "3.0.2", "info": {"title": "Example", "version": "1.0.0"}, "paths": {"/user": {"get": {"summary": "Get user", "responses": {"200": {"description": "successful operation", "content": {"application/json": {"schema": {"type": "object", "properties": {"id": {"type": "integer", "format": "int64"}, "name": {"type": "string", "example": "John Doe"}}}}}}}}}}, "raw_api": {"openapi": "3.0.2", "info": {"version": "1.0.0", "title": "Example"}, "paths": {"/user": {"get": {"summary": "Get user", "responses": {"200": {"description": "successful operation", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}}}}}, "components": {"schemas": {"User": {"type": "object", "properties": {"id": {"type": "integer", "format": "int64"}, "name": {"type": "string", "example": "John Doe"}}}}}}}

```

In the same way,the **raw_api** attribute is exclude by default.

If you want to have it in the output, you can set the **exclude_raw_api** parameter to False.
