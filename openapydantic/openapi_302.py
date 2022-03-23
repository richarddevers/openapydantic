import enum
import typing as t

import pydantic

from openapydantic.common import HTTPStatusCode
from openapydantic.common import MediaType
from openapydantic.common import OpenApi
from openapydantic.common import OpenApiVersion

Field = pydantic.Field

# https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md

Enum = enum.Enum


class BaseModel(pydantic.BaseModel):
    class Config:
        extra = "forbid"
        # extra = "allow"
        # extra = "ignore"


class BaseModelSpecificationExtension(pydantic.BaseModel):
    class Config:
        # extra = "forbid"
        extra = "allow"
        # extra = "ignore"

    @pydantic.root_validator(allow_reuse=True)
    def validate_spec_extension(
        cls,
        values: t.Dict[str, str],
    ) -> t.Dict[str, str]:
        native_attr = set(cls.__fields__.keys())  # all class attr key
        setted_attr = [k for k, v in values.items() if v]  # setted attr key
        extra_attr = [k for k in setted_attr if k not in native_attr]  # difference

        for attr in extra_attr:
            if not attr.startswith("x-"):
                raise ValueError(
                    "Schema extension must be conform to openapi spec extension(^x-)"
                )
        return values


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


class Reference(BaseModel):
    ref: str = Field(
        alias="$ref",
    )


Discriminator = t.Mapping[str, t.Dict[str, str]]


class XML(BaseModel):
    name: t.Optional[str] = None
    namespace: t.Optional[pydantic.AnyUrl] = None
    prefix: t.Optional[str] = None
    attribute: t.Optional[bool] = None
    wrapped: t.Optional[bool] = None


class ExternalDocs(BaseModel):
    description: t.Optional[str] = None
    url: t.Optional[pydantic.AnyUrl] = None


SchemaRef = t.Union["Schema", Reference]


SchemaUnion = t.Union[
    SchemaRef,
    t.Mapping[str, SchemaRef],
]


class Schema(BaseModelSpecificationExtension):
    title: t.Optional[str] = None
    multiple_of: t.Optional[t.List[SchemaUnion]] = Field(
        None,
        alias="multipleOf",
    )
    maximum: t.Optional[int] = None
    exclusive_maximum: t.Optional[t.List[SchemaUnion]] = Field(
        None,
        alias="exclusiveMaximum",
    )
    minimum: t.Optional[int] = None
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
    pattern: t.Optional[t.Pattern] = None
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
    required: t.Optional[t.List[str]] = None
    enum: t.Optional[t.List[str]]
    type: t.Optional[JsonType] = None
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
    items: t.Optional[SchemaUnion] = None
    properties: t.Optional[SchemaUnion] = None
    additional_properties: t.Optional[SchemaUnion] = Field(
        None,
        alias="additionalProperties",
    )
    description: t.Optional[str] = None
    format: t.Optional[str] = None
    default: t.Any
    nullable: t.Optional[bool] = None
    discriminator: t.Optional[Discriminator] = None
    read_only: t.Optional[bool] = Field(
        None,
        alias="readOnly",
    )
    write_only: t.Optional[bool] = Field(
        None,
        alias="writeOnly",
    )
    xml: t.Optional[XML] = None
    external_docs: t.Optional[ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )
    example: t.Any
    deprecated: t.Optional[str] = None


class Example(BaseModel):
    summary: t.Optional[str] = None
    description: t.Optional[str] = None
    value: t.Any
    externalValue: t.Optional[pydantic.AnyUrl] = None


class Header(BaseModel):
    description: t.Optional[str] = None
    required: t.Optional[bool] = None
    deprecated: t.Optional[bool] = None
    allow_empty_value: t.Optional[bool] = Field(
        None,
        alias="allowEmptyValue",
    )
    schema_: t.Optional[SchemaUnion] = Field(
        None,
        alias="schema",
    )


HeadersUnion = t.Optional[t.Mapping[str, t.Union[Header, Reference]]]


class Encoding(BaseModel):
    content_type: t.Optional[t.Union[str, MediaType]] = Field(
        None,
        alias="contentType",
    )
    headers: HeadersUnion
    style: t.Optional[str] = None
    explode: t.Optional[bool] = None
    allow_reserved: t.Optional[bool] = Field(
        None,
        alias="allowReserved",
    )


class MediaTypeObject(pydantic.BaseModel):
    schema_: t.Optional[SchemaUnion] = Field(
        None,
        alias="schema",
    )
    example: t.Any = None
    examples: t.Optional[t.Mapping[str, t.Union[Example, Reference]]] = None
    encoding: t.Optional[t.Mapping[str, t.Union[Encoding, Reference]]] = None


MediaTypeMap = t.Mapping[MediaType, MediaTypeObject]


class Response(BaseModel):
    description: str
    content: t.Optional[MediaTypeMap] = None
    headers: HeadersUnion = None
    links: t.Optional[t.Mapping[str, t.Union["Link", Reference]]] = None


Responses = t.Mapping[HTTPStatusCode, t.Union[Response, Reference]]


class RequestBody(BaseModel):
    description: t.Optional[str] = None
    required: t.Optional[bool] = None
    content: MediaTypeMap


class ServerVariables(BaseModel):
    enum: t.Optional[t.List[str]]
    default: str
    description: t.Optional[str] = None


class Server(BaseModelSpecificationExtension):
    url: t.Optional[str] = None
    description: t.Optional[str] = None
    variables: t.Optional[t.Mapping[str, ServerVariables]] = None


SecurityRequirement = t.Mapping[str, t.List[str]]


class Link(BaseModel):
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
    parameters: t.Optional[t.Mapping[str, t.Any]] = None
    description: t.Optional[str] = None
    server: t.Optional[Server] = None


Response.update_forward_refs()


class Parameter(BaseModel):
    # https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md#parameterObject
    name: str
    in_: str = Field(
        alias="in",
    )
    description: t.Optional[str] = None
    required: t.Optional[bool] = None
    deprecated: t.Optional[bool] = None
    allow_empty_value: t.Optional[bool] = Field(
        None,
        alias="allowEmptyValue",
    )
    schema_: t.Optional[SchemaUnion] = Field(
        None,
        alias="schema",
    )
    style: t.Optional[str] = None
    explode: t.Optional[str] = None
    allow_reserved: t.Optional[bool] = Field(
        None,
        alias="allowReserved",
    )
    example: t.Any
    examples: t.Optional[t.Union[Example, Reference]] = None


Callback = t.Mapping[str, "PathItem"]


class Operation(BaseModelSpecificationExtension):
    tags: t.Optional[t.List[str]] = None
    summary: t.Optional[str] = None
    description: t.Optional[str] = None
    external_docs: t.Optional[ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )
    operation_id: t.Optional[str] = Field(
        None,
        alias="operationId",
    )
    responses: Responses
    parameters: t.Optional[t.List[t.Union[Parameter, Reference]]] = None
    request_body: t.Optional[t.Union[RequestBody, Reference]] = Field(
        None,
        alias="requestBody",
    )
    callbacks: t.Optional[
        t.Union[
            t.Mapping[str, Callback],
            t.Mapping[str, Reference],
        ]
    ] = None
    deprecated: t.Optional[bool] = None
    security: t.Optional[t.List[SecurityRequirement]] = None
    servers: t.Optional[t.List[Server]] = None


class PathItem(BaseModelSpecificationExtension):
    ref: t.Optional[str] = Field(
        None,
        alias="$ref",
    )
    summary: t.Optional[str] = None
    description: t.Optional[str] = None
    get: t.Optional[Operation] = None
    post: t.Optional[Operation] = None
    put: t.Optional[Operation] = None
    path: t.Optional[Operation] = None
    delete: t.Optional[Operation] = None
    head: t.Optional[Operation] = None
    options: t.Optional[Operation] = None
    trace: t.Optional[Operation] = None
    servers: t.Optional[t.List[Server]] = None
    parameters: t.Optional[Reference] = None


Operation.update_forward_refs()


class OAuthFlowImplicit(BaseModel):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]] = None
    authorization_url: pydantic.AnyUrl = Field(alias="authorizationUrl")


class OAuthFlowPassword(BaseModel):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]] = None
    token_url: pydantic.AnyUrl = Field(alias="tokenUrl")


class OAuthFlowClientCredentials(BaseModel):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]] = None
    token_url: pydantic.AnyUrl = Field(alias="tokenUrl")


class OAuthFlowAuthorizationCode(BaseModel):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]] = None
    token_url: pydantic.AnyUrl = Field(alias="tokenUrl")
    authorization_url: pydantic.AnyUrl = Field(alias="authorizationUrl")


class OAuthFlows(BaseModel):
    implicit: t.Optional[OAuthFlowImplicit] = None
    password: t.Optional[OAuthFlowPassword] = None
    client_credentials: t.Optional[OAuthFlowClientCredentials] = Field(
        None,
        alias="clientCredentials",
    )
    authorization_code: t.Optional[OAuthFlowAuthorizationCode] = Field(
        None,
        alias="authorizationCode",
    )


class SecuritySchemeOAuth2(BaseModel):
    type: str = "oauth2"
    description: t.Optional[str] = None
    flows: OAuthFlows


class SecuritySchemeApiKey(BaseModel):
    type: str = "apiKey"
    description: t.Optional[str] = None
    name: str
    in_: SecurityIn = Field(alias="in")


class SecuritySchemeOpenIdConnect(BaseModel):
    type: str = "openIdConnect"
    description: t.Optional[str] = None
    open_id_connect_url: str = Field(alias="openIdConnectUrl")


class SecuritySchemeHttp(BaseModel):
    type: str = "http"
    description: t.Optional[str] = None
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


class Components(BaseModel):
    headers: HeadersUnion
    schemas: t.Optional[t.Mapping[str, t.Union[Schema, Reference]]] = None
    responses: t.Optional[t.Mapping[str, t.Union[Response, Reference]]] = None
    parameters: t.Optional[t.Mapping[str, t.Union[Parameter, Reference]]] = None
    examples: t.Optional[t.Mapping[str, t.Union[Example, Reference]]] = None
    request_bodies: t.Optional[t.Mapping[str, t.Union[RequestBody, Reference]]] = Field(
        None,
        alias="requestBodies",
    )
    links: t.Optional[t.Mapping[str, t.Union[Link, Reference]]] = None
    callbacks: t.Optional[t.Mapping[str, t.Union[Callback, Reference]]] = None
    security_schemes: t.Optional[t.Mapping[str, SecuritySchemeUnion]] = Field(
        None,
        alias="securitySchemes",
    )


Paths = t.Mapping[str, PathItem]


class Contact(BaseModel):
    name: t.Optional[str] = None
    url: t.Optional[pydantic.AnyUrl] = None
    email: t.Optional[pydantic.EmailStr] = None


class License(BaseModel):
    name: str
    url: t.Optional[pydantic.AnyUrl] = None


class Info(BaseModelSpecificationExtension):
    contact: t.Optional[Contact] = None
    description: t.Optional[str]
    license: t.Optional[License] = None
    terms_of_service: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="termsOfService",
    )
    title: str
    version: str


class Tag(BaseModel):
    name: str
    description: t.Optional[str]
    external_docs: t.Optional[ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )


class OpenApi302(OpenApi, BaseModel):
    version: t.ClassVar[OpenApiVersion] = OpenApiVersion.v3_0_2
    components: t.Optional[Components] = None
    openapi: OpenApiVersion
    info: t.Optional[Info] = None
    paths: Paths
    tags: t.Optional[t.List[Tag]] = None
    servers: t.Optional[t.List[Server]] = None
    security: t.Optional[t.List[SecurityRequirement]] = None
    external_docs: t.Optional[ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )
