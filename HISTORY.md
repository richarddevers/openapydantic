# v0.2.3 (2022-04-06)

- folder restructuration
- split integration and unit test
- remove coopling between OpenApi class and ComponentsResolver

# v0.2.2 (2022-04-04)

- References finder now based on jsonpath
- Components consolidation optimization
- If a component self-reference itself, it will not be interpolated (to avoid infinite recursive loop hell)
- Reference format validation is now done during the initial reference listing
- Minor fix
- todo list

# v0.2.1 (2022-03-31)

- Minor fix

# v0.2.0 (2022-03-31)

- References are now interpolated into the final object
- Unit test refactoring
- Big documentation update
- Minor fix

# v0.1.2 (2022-03-25)

- [References](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#referenceObject)  validation.
References format are validate using pydantic validator. Reference path resolution is a custom process performed after pydantic initialization. File reference are currently not managed.
- Unit tests refactoring
- Minor fix

# v0.1.1 (2022-03-23)

Initial release.

- Support of openapi specification version 3.0.2
