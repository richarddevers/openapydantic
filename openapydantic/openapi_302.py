import enum
import functools
import typing as t

import pydantic
from inflection import underscore

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

    @pydantic.validator("ref")
    def validate_reference(cls, v: str) -> str:
        if ".yaml" in v or ".json" in v:
            raise NotImplementedError("Field reference currently not implemented")
        if not v.startswith("#/"):
            raise ValueError(f"reference {v} has invalid format")
        return v


Discriminator = t.Mapping[str, t.Dict[str, str]]


class XML(BaseModel):
    name: t.Optional[str]
    namespace: t.Optional[pydantic.AnyUrl]
    prefix: t.Optional[str]
    attribute: t.Optional[bool]
    wrapped: t.Optional[bool]


class ExternalDocs(BaseModel):
    description: t.Optional[str]
    url: t.Optional[pydantic.AnyUrl]


SchemaRef = t.Union["Schema", Reference]


SchemaUnion = t.Union[
    SchemaRef,
    t.Mapping[str, SchemaRef],
]


class Schema(BaseModelSpecificationExtension):
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


class Example(BaseModel):
    summary: t.Optional[str]
    description: t.Optional[str]
    value: t.Any
    externalValue: t.Optional[pydantic.AnyUrl]


class Header(BaseModel):
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


HeadersUnion = t.Optional[t.Mapping[str, t.Union[Header, Reference]]]


class Encoding(BaseModel):
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
    examples: t.Optional[t.Mapping[str, t.Union[Example, Reference]]]
    encoding: t.Optional[t.Mapping[str, t.Union[Encoding, Reference]]]


MediaTypeMap = t.Mapping[MediaType, MediaTypeObject]


class Response(BaseModel):
    description: str
    content: t.Optional[MediaTypeMap]
    headers: HeadersUnion
    links: t.Optional[t.Mapping[str, t.Union["Link", Reference]]]


Responses = t.Mapping[HTTPStatusCode, t.Union[Response, Reference]]


class RequestBody(BaseModel):
    description: t.Optional[str]
    required: t.Optional[bool]
    content: MediaTypeMap


class ServerVariables(BaseModel):
    enum: t.Optional[t.List[str]]
    default: str
    description: t.Optional[str]


class Server(BaseModelSpecificationExtension):
    url: t.Optional[str]
    description: t.Optional[str]
    variables: t.Optional[t.Mapping[str, ServerVariables]]


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
    parameters: t.Optional[t.Mapping[str, t.Any]]
    description: t.Optional[str]
    server: t.Optional[Server]


Response.update_forward_refs()


class Parameter(BaseModel):
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
    examples: t.Optional[t.Union[Example, Reference]]


Callback = t.Mapping[str, "PathItem"]


class Operation(BaseModelSpecificationExtension):
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
    responses: Responses
    parameters: t.Optional[t.List[t.Union[Parameter, Reference]]]
    request_body: t.Optional[t.Union[RequestBody, Reference]] = Field(
        None,
        alias="requestBody",
    )
    callbacks: t.Optional[
        t.Union[
            t.Mapping[str, Callback],
            t.Mapping[str, Reference],
        ]
    ]
    deprecated: t.Optional[bool]
    security: t.Optional[t.List[SecurityRequirement]]
    servers: t.Optional[t.List[Server]]


class PathItem(BaseModelSpecificationExtension):
    ref: t.Optional[str] = Field(
        None,
        alias="$ref",
    )
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
    parameters: t.Optional[Reference]


Operation.update_forward_refs()


class OAuthFlowImplicit(BaseModel):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]]
    authorization_url: pydantic.AnyUrl = Field(alias="authorizationUrl")


class OAuthFlowPassword(BaseModel):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]]
    token_url: pydantic.AnyUrl = Field(alias="tokenUrl")


class OAuthFlowClientCredentials(BaseModel):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]]
    token_url: pydantic.AnyUrl = Field(alias="tokenUrl")


class OAuthFlowAuthorizationCode(BaseModel):
    refresh_url: t.Optional[pydantic.AnyUrl] = Field(
        None,
        alias="refreshUrl",
    )
    scopes: t.Optional[t.Dict[str, str]]
    token_url: pydantic.AnyUrl = Field(alias="tokenUrl")
    authorization_url: pydantic.AnyUrl = Field(alias="authorizationUrl")


class OAuthFlows(BaseModel):
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


class SecuritySchemeOAuth2(BaseModel):
    type: str = "oauth2"
    description: t.Optional[str]
    flows: OAuthFlows


class SecuritySchemeApiKey(BaseModel):
    type: str = "apiKey"
    description: t.Optional[str]
    name: str
    in_: SecurityIn = Field(alias="in")


class SecuritySchemeOpenIdConnect(BaseModel):
    type: str = "openIdConnect"
    description: t.Optional[str]
    open_id_connect_url: str = Field(alias="openIdConnectUrl")


class SecuritySchemeHttp(BaseModel):
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


class Components(BaseModel):
    headers: HeadersUnion
    schemas: t.Optional[t.Mapping[str, t.Union[Schema, Reference]]]
    responses: t.Optional[t.Mapping[str, t.Union[Response, Reference]]]
    parameters: t.Optional[t.Mapping[str, t.Union[Parameter, Reference]]]
    examples: t.Optional[t.Mapping[str, t.Union[Example, Reference]]]
    request_bodies: t.Optional[t.Mapping[str, t.Union[RequestBody, Reference]]] = Field(
        None,
        alias="requestBodies",
    )
    links: t.Optional[t.Mapping[str, t.Union[Link, Reference]]]
    callbacks: t.Optional[t.Mapping[str, t.Union[Callback, Reference]]]
    security_schemes: t.Optional[t.Mapping[str, SecuritySchemeUnion]] = Field(
        None,
        alias="securitySchemes",
    )


Paths = t.Mapping[str, PathItem]


class Contact(BaseModel):
    name: t.Optional[str]
    url: t.Optional[pydantic.AnyUrl]
    email: t.Optional[pydantic.EmailStr]


class License(BaseModel):
    name: str
    url: t.Optional[pydantic.AnyUrl]


class Info(BaseModelSpecificationExtension):
    contact: t.Optional[Contact]
    description: t.Optional[str]
    license: t.Optional[License]
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


AllClass = t.Union[
    Components,
    Contact,
    Encoding,
    Example,
    ExternalDocs,
    Header,
    Info,
    License,
    Link,
    MediaTypeObject,
    OAuthFlowAuthorizationCode,
    OAuthFlowClientCredentials,
    OAuthFlowImplicit,
    OAuthFlowPassword,
    OAuthFlows,
    Operation,
    Parameter,
    PathItem,
    RequestBody,
    Response,
    Schema,
    SecuritySchemeApiKey,
    SecuritySchemeHttp,
    SecuritySchemeOAuth2,
    SecuritySchemeOpenIdConnect,
    Server,
    ServerVariables,
    Tag,
    XML,
]


class OpenApi302(OpenApi, BaseModel):
    version: t.ClassVar[OpenApiVersion] = OpenApiVersion.v3_0_2
    components: t.Optional[Components]
    openapi: OpenApiVersion
    info: Info
    paths: Paths
    tags: t.Optional[t.List[Tag]]
    servers: t.Optional[t.List[Server]]
    security: t.Optional[t.List[SecurityRequirement]]
    external_docs: t.Optional[ExternalDocs] = Field(
        None,
        alias="externalDocs",
    )
    __ref__: t.Optional[t.List[str]]

    def _list_reference(self, obj: t.Any):
        if isinstance(obj, Reference):
            self.__ref__.append(obj.ref)  # type: ignore
            return

        if isinstance(obj, pydantic.AnyUrl) or isinstance(obj, pydantic.EmailStr):
            return

        if isinstance(obj, list):
            for attr in obj:  # type: ignore
                self._list_reference(attr)
            return

        if isinstance(obj, dict):
            for attr in obj:  # type: ignore
                self._list_reference(obj.get(attr))  # type: ignore
            return

        for typ in AllClass.__args__:  # type: ignore
            if isinstance(obj, typ):
                for attr in obj.__fields_set__:  # type: ignore
                    sub_obj = getattr(obj, attr)  # type: ignore
                    self._list_reference(sub_obj)

    def _resolve_reference(self):
        def _getattr(obj, attr):  # type: ignore

            # _attr is needed for snake_case aliased attr
            _attr = underscore(attr) if isinstance(attr, str) else attr  # type: ignore
            if _attr != attr and hasattr(obj, _attr):  # type: ignore
                return getattr(obj, _attr)  # type: ignore

            if hasattr(obj, attr):  # type: ignore
                return getattr(obj, attr)  # type: ignore

            if isinstance(obj, dict) and attr in obj.keys():
                return obj.get(attr)  # type: ignore

            raise ValueError(f"Reference invalid. {attr} not found")

        for ref in self.__ref__:  # type: ignore
            unprefix_ref = ref.split("/")[1:]
            unprefix_ref.insert(0, self)  # type: ignore
            functools.reduce(_getattr, unprefix_ref)  # type: ignore

    def __init__(self, **data) -> None:  # type: ignore
        super().__init__(**data)
        object.__setattr__(self, "__ref__", [])
        for attr in self.__fields_set__:
            obj = getattr(self, attr)
            self._list_reference(obj)

        self._resolve_reference()
