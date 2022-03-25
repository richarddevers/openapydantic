# v0.1.2 (2022-03-25)

References & unit tests refactoring

## Highlights

* [References](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#referenceObject) validation.
References format are validate using pydantic validator. Reference path resolution is a custom process performed after pydantic initialization. File reference are currently not managed.

# v0.1.1 (2022-03-23)

Initial release.

## Highlights

* Support of openapi specification version 3.0.2