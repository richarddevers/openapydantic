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


class ComponentType(enum.Enum):
    schemas = "schemas"
    headers = "headers"
    responses = "responses"
    parameters = "parameters"
    examples = "examples"
    request_bodies = "requestBodies"
    links = "links"
    callbacks = "callbacks"


class ComponentsParser:
    with_ref = {}
    without_ref = {}
    ref_find = False
    ref_path = []
    current_obj = None

    @staticmethod
    def validate_ref(ref: str) -> None:
        if ".yaml" in ref or ".json" in ref:
            raise NotImplementedError("File reference not implemented")
        if not ref.startswith("#/"):
            raise ValueError(f"reference {ref} has invalid format")

    @classmethod
    def find_ref(
        cls,
        *,
        obj: t.Any,
    ):
        if isinstance(obj, list):
            for elt in enumerate(obj):
                cls.find_ref(obj=elt)

        if isinstance(obj, dict):
            ref = obj.get("$ref")
            if ref:
                cls.validate_ref(ref=ref)
                cls.ref_find = True

            for key, data in obj.items():
                cls.find_ref(obj=obj.get(key))

    @classmethod
    def search_schemas_for_ref(
        cls,
        *,
        schemas: t.Dict[str, t.Any],
    ):

        for key, data in schemas.items():
            cls.ref_find = False
            cls.find_ref(
                obj=data,
            )

            if cls.ref_find:
                cls.with_ref[ComponentType.schemas.name][key] = data
            else:
                cls.without_ref[ComponentType.schemas.name][key] = data

    @classmethod
    def parser(
        cls,
        *,
        raw_api: t.Dict[str, t.Any],
    ):
        cls.with_ref[ComponentType.schemas.name] = {}
        cls.without_ref[ComponentType.schemas.name] = {}

        components = raw_api.get("components")
        if not components:
            print("No components in this api")
            return

        schemas = components.get("schemas")
        if not schemas:
            print("No schemas in components section")
            return
        cls.search_schemas_for_ref(schemas=schemas)

    ########

    @staticmethod
    def get_ref_data(ref: str) -> t.Tuple[ComponentType, str]:
        ref_split = ref.split("/")  # format #/components/schemas/Pet
        ref_type = ComponentType(ref_split[2])
        ref_key = ref_split[-1]
        return ref_type, ref_key


class RefModel(pydantic.BaseModel):
    ref: t.Optional[str] = Field(None, alias="$ref")


class BaseModel(RefModel):
    class Config:
        extra = "forbid"
        # extra = "allow"
        # extra = "ignore"


class BaseModelSpecificationExtension(RefModel):
    class Config:
        # extra = "forbid"
        extra = "allow"
        # extra = "ignore"

    @pydantic.root_validator(pre=True, allow_reuse=True)
    def validate_root(
        cls,
        values: t.Dict[str, str],
    ) -> t.Dict[str, str]:
        # check ref
        ref = values.get("$ref")
        if ref:
            ref_type, ref_key = ComponentsParser.get_ref_data(ref)
            ref_found = ComponentsParser.without_ref[ref_type.name].get(ref_key)

            if not ref_found:
                raise ValueError(f"Reference not found:{ref_type}/{ref_key}")

            return ref_found
        else:
            # check spec extension:
            native_attr = set(cls.__fields__.keys())  # all class attr key
            setted_attr = [k for k, v in values.items() if v]  # setted attr key
            extra_attr = [k for k in setted_attr if k not in native_attr]  # difference
            clean_extra_attr = list(filter(lambda x: (x != "$ref"), extra_attr))
            for attr in clean_extra_attr:
                if not attr.startswith("x-"):
                    raise ValueError(
                        f"Schema extension:{attr} must be conform to openapi spec extension(^x-)"
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


SchemaUnion = t.Union[
    "Schema",
    t.Mapping[str, "Schema"],
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


HeadersUnion = t.Optional[t.Mapping[str, Header]]


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
    examples: t.Optional[t.Mapping[str, Example]]
    encoding: t.Optional[t.Mapping[str, Encoding]]


MediaTypeMap = t.Mapping[MediaType, MediaTypeObject]


class Response(BaseModel):
    description: str
    content: t.Optional[MediaTypeMap]
    headers: HeadersUnion
    links: t.Optional[t.Mapping[str, "Link"]]


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
    examples: t.Optional[Example]


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


class PathItem(BaseModelSpecificationExtension):
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
    parameters: t.Optional[t.Any]


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
    # Components,
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
    __version__: t.ClassVar[OpenApiVersion] = OpenApiVersion.v3_0_2
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

    def as_clean_json(self):
        return self.json(
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
        )

    def __init__(self, **data) -> None:  # type: ignore
        ComponentsParser.parser(raw_api=data)
        super().__init__(**data)  # type: ignore
        object.__setattr__(self, "__ref__", {})
