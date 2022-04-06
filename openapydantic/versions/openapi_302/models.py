import enum
import typing as t

import pydantic

from openapydantic import common
from openapydantic import resolver

HTTPStatusCode = common.HTTPStatusCode
MediaType = common.MediaType
OpenApiBaseModel = common.OpenApiBaseModel
ComponentType = common.ComponentType

Field = pydantic.Field


def reference_interpolation(
    values: t.Dict[str, t.Any],
) -> t.Dict[str, t.Any]:
    ref = values.get("$ref")
    # print("====== VALIDATE ROOT ======")
    # print(f"ref:{ref}")
    if ref:
        # Avoir self reference here
        if ref in resolver.ComponentsResolver.self_ref:
            return values
        ref_type, ref_key = resolver.get_ref_data(
            ref=ref,
        )
        # print(f"ref_type:{ref_type.name}")
        # print(f"ref_key:{ref_key}")
        ref_found: t.Dict[str, t.Any] = resolver.ComponentsResolver.without_ref[
            ref_type.name
        ].get(ref_key)
        # print(f"ref_found:{ref_found}")
        if not ref_found:
            raise ValueError(f"Reference not found:{ref_type}/{ref_key}")

        return ref_found
    return values


class RefModel(OpenApiBaseModel):
    ref: t.Optional[str] = Field(
        None,
        alias="$ref",
    )

    @pydantic.root_validator(
        pre=True,
        allow_reuse=True,
    )
    def _reference_interpolation(
        cls,
        values: t.Dict[str, str],
    ) -> t.Dict[str, t.Any]:
        return reference_interpolation(
            values=values,
        )


class BaseModelForbid(RefModel):
    class Config:
        extra = "forbid"


class BaseModelAllow(RefModel):
    class Config:
        extra = "allow"


class JsonType(enum.Enum):
    integer = "integer"
    string = "string"
    array = "array"
    object_ = "object"
    boolean = "boolean"
    number = "number"


class SecurityIn(enum.Enum):
    query = "query"
    header = "header"
    cookie = "cookie"


Discriminator = t.Mapping[str, t.Dict[str, str]]


class XML(BaseModelForbid):
    name: t.Optional[str]
    namespace: t.Optional[pydantic.AnyUrl]
    prefix: t.Optional[str]
    attribute: t.Optional[bool]
    wrapped: t.Optional[bool]


class ExternalDocs(BaseModelForbid):
    description: t.Optional[str]
    url: t.Optional[pydantic.AnyUrl]


SchemaUnion = t.Union[
    t.Mapping[str, "Schema"],
    "Schema",
]


class Schema(BaseModelAllow):
    title: t.Optional[str]
    multiple_of: t.Optional[t.List[SchemaUnion]] = Field(
        None,
        alias="multipleOf",
    )
    maximum: t.Optional[int]
    exclusive_maximum: t.Optional[t.List[SchemaUnion]] = Field(
        None,
        alias="exclusiveMaximum",
    )
    minimum: t.Optional[int]
    exclusive_minimum: t.Optional[t.List[SchemaUnion]] = Field(
        None,
        alias="exclusiveMinimum",
    )
    max_length: t.Optional[int] = Field(
        None,
        alias="maxLength",
    )
    min_length: t.Optional[int] = Field(
        None,
        alias="minLength",
    )
    pattern: t.Optional[t.Pattern]
    max_items: t.Optional[int] = Field(
        None,
        alias="maxItems",
    )
    min_items: t.Optional[int] = Field(
        None,
        alias="minItems",
    )
    unique_items: t.Optional[t.Any] = Field(
        None,
        alias="uniqueItems",
    )
    max_properties: t.Optional[int] = Field(
        None,
        alias="maxProperties",
    )
    min_properties: t.Optional[int] = Field(
        None,
        alias="minProperties",
    )
    required: t.Optional[t.List[str]]
    enum: t.Optional[t.List[str]]
    type: t.Optional[JsonType]
    all_of: t.Optional[t.List[SchemaUnion]] = Field(
        None,
        alias="allOf",
    )
    one_of: t.Optional[t.List[SchemaUnion]] = Field(
        None,
        alias="oneOf",
    )
    any_of: t.Optional[t.List[SchemaUnion]] = Field(
        None,
        alias="anyOf",
    )
    not_: t.Optional[t.List[SchemaUnion]] = Field(
        None,
        alias="not",
    )
    items: t.Optional[SchemaUnion]
    properties: t.Optional[SchemaUnion]
    additional_properties: t.Optional[SchemaUnion] = Field(
        None,
        alias="additionalProperties",
    )
    description: t.Optional[str]
    format: t.Optional[str]
    default: t.Any
    nullable: t.Optional[bool]
    discriminator: t.Optional[Discriminator]
    read_only: t.Optional[bool] = Field(
        None,
        alias="readOnly",
    )
    write_only: t.Optional[bool] = Field(
        None,
        alias="writeOnly",
    )
    xml: t.Optional[XML]
    external_docs: t.Optional[ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )
    example: t.Any
    deprecated: t.Optional[str]


class Example(BaseModelAllow):
    summary: t.Optional[str]
    description: t.Optional[str]
    value: t.Any
    externalValue: t.Optional[pydantic.AnyUrl]


class Header(BaseModelForbid):
    description: t.Optional[str]
    required: t.Optional[bool]
    deprecated: t.Optional[bool]
    allow_empty_value: t.Optional[bool] = Field(
        None,
        alias="allowEmptyValue",
    )
    schema_: t.Optional[SchemaUnion] = Field(
        None,
        alias="schema",
    )


HeadersUnion = t.Optional[t.Mapping[str, Header]]


class Encoding(BaseModelForbid):
    content_type: t.Optional[t.Union[str, MediaType]] = Field(
        None,
        alias="contentType",
    )
    headers: HeadersUnion
    style: t.Optional[str]
    explode: t.Optional[bool]
    allow_reserved: t.Optional[bool] = Field(
        None,
        alias="allowReserved",
    )


class MediaTypeObject(pydantic.BaseModel):
    schema_: t.Optional[SchemaUnion] = Field(
        None,
        alias="schema",
    )
    example: t.Any
    examples: t.Optional[t.Mapping[str, Example]]
    encoding: t.Optional[t.Mapping[str, Encoding]]


MediaTypeMap = t.Mapping[MediaType, MediaTypeObject]


class Response(BaseModelForbid):
    description: str
    content: t.Optional[MediaTypeMap]
    headers: HeadersUnion
    links: t.Optional[t.Mapping[str, "Link"]]


class RequestBody(BaseModelForbid):
    description: t.Optional[str]
    required: t.Optional[bool]
    content: t.Optional[MediaTypeMap]


class ServerVariables(BaseModelForbid):
    enum: t.Optional[t.List[str]]
    default: str
    description: t.Optional[str]


class Server(BaseModelAllow):
    url: t.Optional[str]
    description: t.Optional[str]
    variables: t.Optional[t.Mapping[str, ServerVariables]]


SecurityRequirement = t.Mapping[str, t.List[str]]


class Link(BaseModelForbid):
    operation_ref: t.Optional[str] = Field(
        None,
        alias="operationRef",
    )
    operation_id: t.Optional[str] = Field(
        None,
        alias="operationId",
    )
    request_body: t.Optional[t.Any] = Field(
        None,
        alias="requestBody",
    )
    parameters: t.Optional[t.Mapping[str, t.Any]]
    description: t.Optional[str]
    server: t.Optional[Server]


Response.update_forward_refs()


class Parameter(BaseModelForbid):
    # https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#parameterObject
    name: str
    in_: str = Field(
        alias="in",
    )
    description: t.Optional[str]
    required: t.Optional[bool]
    deprecated: t.Optional[bool]
    allow_empty_value: t.Optional[bool] = Field(
        None,
        alias="allowEmptyValue",
    )
    schema_: t.Optional[SchemaUnion] = Field(
        None,
        alias="schema",
    )
    style: t.Optional[str]
    explode: t.Optional[str]
    allow_reserved: t.Optional[bool] = Field(
        None,
        alias="allowReserved",
    )
    example: t.Any
    examples: t.Optional[Example]


Callback = t.Mapping[str, "PathItem"]


class Operation(BaseModelAllow):
    tags: t.Optional[t.List[str]]
    summary: t.Optional[str]
    description: t.Optional[str]
    external_docs: t.Optional[ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )
    operation_id: t.Optional[str] = Field(
        None,
        alias="operationId",
    )
    responses: t.Mapping[HTTPStatusCode, Response]
    parameters: t.Optional[t.List[Parameter]]
    request_body: t.Optional[RequestBody] = Field(
        None,
        alias="requestBody",
    )
    callbacks: t.Optional[t.Mapping[str, Callback]]
    deprecated: t.Optional[bool]
    security: t.Optional[t.List[SecurityRequirement]]
    servers: t.Optional[t.List[Server]]


class PathItem(BaseModelAllow):
    summary: t.Optional[str]
    description: t.Optional[str]
    get: t.Optional[Operation]
    post: t.Optional[Operation]
    put: t.Optional[Operation]
    path: t.Optional[Operation]
    delete: t.Optional[Operation]
    head: t.Optional[Operation]
    options: t.Optional[Operation]
    trace: t.Optional[Operation]
    servers: t.Optional[t.List[Server]]
    parameters: t.Optional[t.List[Parameter]]


Operation.update_forward_refs()


class OAuthFlowImplicit(BaseModelForbid):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]]
    authorization_url: pydantic.AnyUrl = Field(alias="authorizationUrl")


class OAuthFlowPassword(BaseModelForbid):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]]
    token_url: pydantic.AnyUrl = Field(alias="tokenUrl")


class OAuthFlowClientCredentials(BaseModelForbid):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]]
    token_url: pydantic.AnyUrl = Field(alias="tokenUrl")


class OAuthFlowAuthorizationCode(BaseModelForbid):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]]
    token_url: pydantic.AnyUrl = Field(alias="tokenUrl")
    authorization_url: pydantic.AnyUrl = Field(alias="authorizationUrl")


class OAuthFlows(BaseModelForbid):
    implicit: t.Optional[OAuthFlowImplicit]
    password: t.Optional[OAuthFlowPassword]
    client_credentials: t.Optional[OAuthFlowClientCredentials] = Field(
        None,
        alias="clientCredentials",
    )
    authorization_code: t.Optional[OAuthFlowAuthorizationCode] = Field(
        None,
        alias="authorizationCode",
    )


class SecuritySchemeOAuth2(BaseModelForbid):
    type: str = "oauth2"
    description: t.Optional[str]
    flows: OAuthFlows


class SecuritySchemeApiKey(BaseModelForbid):
    type: str = "apiKey"
    description: t.Optional[str]
    name: str
    in_: SecurityIn = Field(alias="in")


class SecuritySchemeOpenIdConnect(BaseModelForbid):
    type: str = "openIdConnect"
    description: t.Optional[str]
    open_id_connect_url: str = Field(alias="openIdConnectUrl")


class SecuritySchemeHttp(BaseModelForbid):
    type: str = "http"
    description: t.Optional[str]
    scheme: str
    bearer_format: t.Optional[str] = Field(
        None,
        alias="bearerFormat",
    )


SecuritySchemeUnion = t.Union[
    SecuritySchemeOAuth2,
    SecuritySchemeApiKey,
    SecuritySchemeOpenIdConnect,
    SecuritySchemeHttp,
]


class Components(BaseModelForbid):
    headers: HeadersUnion
    schemas: t.Optional[t.Mapping[str, Schema]]
    responses: t.Optional[t.Mapping[str, Response]]
    parameters: t.Optional[t.Mapping[str, Parameter]]
    examples: t.Optional[t.Mapping[str, Example]]
    request_bodies: t.Optional[t.Mapping[str, RequestBody]] = Field(
        None,
        alias="requestBodies",
    )
    links: t.Optional[t.Mapping[str, Link]]
    callbacks: t.Optional[t.Mapping[str, Callback]]
    security_schemes: t.Optional[t.Mapping[str, SecuritySchemeUnion]] = Field(
        None,
        alias="securitySchemes",
    )


Paths = t.Mapping[str, PathItem]


class Contact(BaseModelForbid):
    name: t.Optional[str]
    url: t.Optional[pydantic.AnyUrl]
    email: t.Optional[pydantic.EmailStr]


class License(BaseModelForbid):
    name: str
    url: t.Optional[pydantic.AnyUrl]


class Info(BaseModelAllow):
    contact: t.Optional[Contact]
    description: t.Optional[str]
    license: t.Optional[License]
    terms_of_service: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="termsOfService",
    )
    title: str
    version: str


class Tag(BaseModelForbid):
    name: str
    description: t.Optional[str]
    external_docs: t.Optional[ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )
