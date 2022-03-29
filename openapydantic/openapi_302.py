import copy
import enum
import typing as t

import pydantic

import openapydantic

HTTPStatusCode = openapydantic.common.HTTPStatusCode
MediaType = openapydantic.common.MediaType
OpenApi = openapydantic.common.OpenApi
OpenApiVersion = openapydantic.common.OpenApiVersion
Field = pydantic.Field

# https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.2.md


class ComponentType(enum.Enum):
    components = "components"
    schemas = "schemas"
    headers = "headers"
    responses = "responses"
    parameters = "parameters"
    examples = "examples"
    request_bodies = "requestBodies"
    links = "links"
    callbacks = "callbacks"


class RefModel(pydantic.BaseModel):
    ref: t.Optional[str] = Field(
        None,
        alias="$ref",
    )

    def as_clean_json(
        self,
        exclude_components: bool = True,
    ):
        if exclude_components:
            return self.json(
                by_alias=True,
                exclude_unset=True,
                exclude_none=True,
                exclude={ComponentType.components.value},
            )
        return self.json(
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
        )

    def as_clean_dict(
        self,
        exclude_components: bool = True,
    ):
        if exclude_components:
            return self.dict(
                by_alias=True,
                exclude_unset=True,
                exclude_none=True,
                exclude={ComponentType.components.value},
            )
        return self.dict(
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
        )

    @pydantic.root_validator(
        pre=True,
        allow_reuse=True,
    )
    def validate_root(
        cls,
        values: t.Dict[str, str],
    ) -> t.Dict[str, t.Any]:
        ref = values.get("$ref")
        if ref:
            # load reference from ComponentsParser
            ref_type, ref_key = ComponentsParser.get_ref_data(ref)
            ref_found: t.Dict[str, t.Any] = ComponentsParser.without_ref[
                ref_type.name
            ].get(ref_key)

            if not ref_found:
                raise ValueError(f"Reference not found:{ref_type}/{ref_key}")

            return ref_found
        return values

    #     # check spec extension:
    #     native_attr = set(cls.__fields__.keys())  # all class attr key
    #     setted_attr = [k for k, v in values.items() if v]  # setted attr key
    #     extra_attr = [k for k in setted_attr if k not in native_attr]  # difference
    #     clean_extra_attr = list(filter(lambda x: (x != "$ref"), extra_attr))
    #     for attr in clean_extra_attr:
    #         breakpoint()
    #         if not attr.startswith("x-"):
    #             raise ValueError(
    #                 f"Schema extension:{attr} must be conform to openapi "
    #                 f"specication (^x-)"
    #             )
    #     return values


class BaseModelForbid(RefModel):
    class Config:
        extra = "forbid"
        use_enum_values = True


class BaseModelAllow(RefModel):
    class Config:
        extra = "allow"
        use_enum_values = True


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


class Example(BaseModelForbid):
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
    parameters: t.Optional[t.Any]


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


AllClass = t.Union[
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


class ComponentsParser:
    with_ref: t.Dict[str, t.Any] = {}
    without_ref: t.Dict[str, t.Any] = {}
    ref_find = False
    raw_api = {}

    @classmethod
    def reset(cls):
        cls.with_ref = {}
        cls.without_ref = {}
        cls.ref_find = False
        cls.raw_api = {}

    @staticmethod
    def get_ref_data(ref: str) -> t.Tuple[ComponentType, str]:
        ref_split = ref.split("/")  # format #/components/schemas/Pet
        ref_type = ComponentType(ref_split[2])
        ref_key = ref_split[-1]
        return ref_type, ref_key

    @staticmethod
    def _validate_ref(ref: str) -> None:
        if ".yaml" in ref or ".json" in ref:
            raise NotImplementedError("File reference not implemented")
        if not ref.startswith("#/"):
            raise ValueError(f"reference {ref} has invalid format")

    @classmethod
    def _find_ref(
        cls,
        *,
        obj: t.Any,
    ):
        if isinstance(obj, list):
            for elt in obj:  # type: ignore
                cls._find_ref(obj=elt)

        if isinstance(obj, dict):
            ref = obj.get("$ref")  # type: ignore
            if ref:
                cls._validate_ref(ref=ref)  # type: ignore
                cls.ref_find = True

            for key in obj:  # type: ignore
                cls._find_ref(obj=obj.get(key))  # type: ignore

    @classmethod
    def _search_component_for_ref(
        cls,
        *,
        key: str,
        value: t.Dict[str, t.Any],
        component_type: ComponentType,
    ):
        cls.ref_find = False
        cls._find_ref(
            obj=value,
        )

        if cls.ref_find:
            cls.with_ref[component_type.name][key] = value
        else:
            cls.without_ref[component_type.name][key] = value

    @classmethod
    def _search_components_for_ref(
        cls,
        *,
        components: t.Dict[str, t.Any],
        component_type: ComponentType,
    ):
        for key, value in components.items():
            cls._search_component_for_ref(
                key=key,
                value=value,
                component_type=component_type,
            )

    @classmethod
    def _consolidate_components(
        cls,
        component_type: ComponentType,
    ) -> None:
        component_dict = {}
        component_key = component_type.name
        with_ref_copy = copy.deepcopy(cls.with_ref[component_key])
        for key, value in with_ref_copy.items():
            cls.ref_find = False

            if component_type == ComponentType.schemas:
                component = Schema(**value)
            elif component_type == ComponentType.request_bodies:
                component = RequestBody(**value)

            component_dict = component.as_clean_dict()  # type: ignore
            cls._search_component_for_ref(
                key=key,
                value=component_dict,
                component_type=component_type,
            )

            if cls.ref_find:
                cls.with_ref[component_key][key] = component_dict
                cls._consolidate_components(component_type=component_type)
            else:
                cls.without_ref[component_key][key] = component_dict
                del cls.with_ref[component_key][key]
                if not len(cls.with_ref):
                    break

    @classmethod
    def parse(
        cls,
        *,
        raw_api: t.Dict[str, t.Any],
    ):
        cls.with_ref[ComponentType.schemas.name] = {}
        cls.without_ref[ComponentType.schemas.name] = {}
        cls.with_ref[ComponentType.request_bodies.name] = {}
        cls.without_ref[ComponentType.request_bodies.name] = {}

        components = raw_api.get(ComponentType.components.value)
        if not components:
            print("No components in this api")
            return

        schemas = components.get(ComponentType.schemas.value)
        request_bodies = components.get(ComponentType.request_bodies.value)

        if schemas:
            cls._search_components_for_ref(
                components=schemas,
                component_type=ComponentType.schemas,
            )

        if request_bodies:
            cls._search_components_for_ref(
                components=request_bodies,
                component_type=ComponentType.request_bodies,
            )

        if schemas:
            cls._consolidate_components(component_type=ComponentType.schemas)

        if request_bodies:
            cls._consolidate_components(component_type=ComponentType.request_bodies)


class OpenApi302(OpenApi, BaseModelForbid):
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

    def __init__(self, **data: t.Any) -> None:
        ComponentsParser.parse(raw_api=data)
        super().__init__(**data)
