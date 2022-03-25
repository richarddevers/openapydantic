# v0.1.2 (2022-03-25)

- [References](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#referenceObject)  validation.
References format are validate using pydantic validator. Reference path resolution is a custom process performed after pydantic initialization. File reference are currently not managed.
- Unit tests refactoring
- Minor fix

# v0.1.1 (2022-03-23)

Initial release.

- Support of openapi specification version 3.0.2
