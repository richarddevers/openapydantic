import enum
import typing as t

raw_api = {
    "openapi": "3.0.0",
    "servers": [],
    "info": {
        "description": "This is a simple API",
        "version": "1.0.0",
        "title": "Simple Inventory API",
        "contact": {"email": "you@your-company.com"},
        "license": {
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html",
        },
    },
    "tags": [
        {"name": "admins", "description": "Secured Admin-only calls"},
        {
            "name": "developers",
            "description": "Operations available to regular developers",
        },
    ],
    "paths": {
        "/inventory": {
            "get": {
                "tags": ["developers"],
                "summary": "searches inventory",
                "operationId": "searchInventory",
                "description": "By passing in the appropriate options, you can search for\navailable inventory in the system\n",
                "parameters": [
                    {
                        "in": "query",
                        "name": "searchString",
                        "description": "pass an optional search string for looking up inventory",
                        "required": False,
                        "schema": {"type": "string"},
                    },
                    {
                        "in": "query",
                        "name": "skip",
                        "description": "number of records to skip for pagination",
                        "schema": {"type": "integer", "format": "int32", "minimum": 0},
                    },
                    {
                        "in": "query",
                        "name": "limit",
                        "description": "maximum number of records to return",
                        "schema": {
                            "type": "integer",
                            "format": "int32",
                            "minimum": 0,
                            "maximum": 50,
                        },
                    },
                ],
                "responses": {
                    "200": {
                        "description": "search results matching criteria",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/InventoryItem"
                                    },
                                }
                            }
                        },
                    },
                    "400": {"description": "bad input parameter"},
                },
            },
            "post": {
                "tags": ["admins"],
                "summary": "adds an inventory item",
                "operationId": "addInventory",
                "description": "Adds an item to the system",
                "responses": {
                    "201": {"description": "item created"},
                    "400": {"description": "invalid input, object invalid"},
                    "409": {"description": "an existing item already exists"},
                },
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/InventoryItem"}
                        }
                    },
                    "description": "Inventory item to add",
                },
            },
        }
    },
    "components": {
        "schemas": {
            "InventoryItem": {
                "type": "object",
                "required": ["id", "name", "manufacturer", "releaseDate"],
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "example": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    },
                    "name": {"type": "string", "example": "Widget Adapter"},
                    "releaseDate": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2016-08-29T09:12:33.001Z",
                    },
                    "manufacturer": {"$ref": "#/components/schemas/Manufacturer"},
                },
            },
            "Manufacturer": {
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "example": "ACME Corporation"},
                    "homePage": {
                        "type": "string",
                        "format": "url",
                        "example": "https://www.acme-corp.com",
                    },
                    "phone": {"type": "string", "example": "408-867-5309"},
                },
                "type": "object",
            },
        }
    },
}


class ComponentType(enum.Enum):
    schemas = "Schemas"
    headers = "Headers"
    responses = "Responses"
    parameters = "Parameters"
    examples = "Examples"
    request_bodies = "RequestBodies"
    links = "Links"
    callbacks = "Callbacks"


class ComponentsParser:
    components_with_ref = {}
    components_without_ref = {}
    ref_find = False

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
            for elt in obj:
                cls.find_ref(obj=elt)

        if isinstance(obj, dict):
            ref = obj.get("$ref")
            if ref:
                cls.validate_ref(ref=ref)
                cls.ref_find = True
            for key, data in obj.items():
                cls.find_ref(obj=obj.get(key))

    @classmethod
    def parse_schemas(
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
                cls.components_with_ref[ComponentType.schemas.name][key] = data
            else:
                cls.components_without_ref[ComponentType.schemas.name][key] = data

    @classmethod
    def parser(
        cls,
        *,
        raw_api: t.Dict[str, t.Any],
    ):
        cls.components_with_ref[ComponentType.schemas.name] = {}
        cls.components_without_ref[ComponentType.schemas.name] = {}

        components = raw_api.get("components")
        if not components:
            print("No components in this api")
            return

        schemas = components.get("schemas")
        if not schemas:
            print("No schemas in components section")
            return
        cls.parse_schemas(schemas=schemas)


ComponentsParser.parser(raw_api=raw_api)
print(len(ComponentsParser.components_with_ref["schemas"]))
print(len(ComponentsParser.components_without_ref["schemas"]))
breakpoint()
