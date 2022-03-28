import copy
import enum
import typing as t

import pydantic

raw_api = {
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
    schemas = "schemas"
    headers = "headers"
    responses = "responses"
    parameters = "parameters"
    examples = "examples"
    request_bodies = "requestBodies"
    links = "links"
    callbacks = "callbacks"


class ComponentsParser:
    components_with_ref = {}
    components_without_ref = {}
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
        cls.search_schemas_for_ref(schemas=schemas)

    ########

    @staticmethod
    def get_ref_data(ref: str) -> t.Tuple[ComponentType, str]:
        ref_split = ref.split("/")  # format #/components/schemas/Pet
        ref_type = ComponentType(ref_split[2])
        ref_key = ref_split[-1]
        return ref_type, ref_key

        # def find_ref2(
        #     *,
        #     obj: t.Any,
        # ):
        #     if isinstance(obj, list):
        #         for elt in obj:
        #             find_ref2(obj=elt)

        #     if isinstance(obj, dict, current_obj:dict):
        #         ref = obj.get("$ref")
        #         if ref:
        #             ref_type, ref_key = get_ref_data(ref)
        #             ref_found = cls.components_without_ref[ref_type.name].get(ref_key)
        #             if ref_found:
        #                 new_obj = cls.components_with_ref[ref_type.name][key]

        #                 obj = tmp

        #                 cls.components_with_ref[ref_type.name].pop(key)
        #                 breakpoint()
        #         else:
        #             for key2 in obj:
        #                 find_ref2(obj=obj.get(key2))

        # with_ref = copy.deepcopy(cls.components_with_ref["schemas"])

        # while len(with_ref):
        #     for key, data in cls.components_with_ref["schemas"]:
        #         current_obj = {key: data}
        #         find_ref2(obj=data)

        #         cls.ref_find = False
        #         cls.find_ref(obj=data)
        #         if cls.ref_find:
        #             cls.components_with_ref[ComponentType.schemas.name][key] = data
        #         else:
        #             cls.components_without_ref[ComponentType.schemas.name][key] = data
        #     print(cls.components_with_ref)
        #     with_ref = copy.deepcopy(cls.components_with_ref["schemas"])
        #     print(len(with_ref))


class Schema(pydantic.BaseModel):
    type: str
    properties: t.Optional["Schema"] = pydantic.Field(None)
    ref: t.Optional[str] = pydantic.Field(
        None,
        alias="$ref",
    )

    @pydantic.root_validator(pre=True)
    def ref_loader(cls, values):
        ref = values.get("$ref")
        if not ref:
            return values

        ref_type, ref_key = ComponentsParser.get_ref_data(ref)
        ref_found = cls.components_without_ref[ref_type.name].get(ref_key)

        if not ref_found:
            raise f"Reference not found:{ref_type}/{ref_key}"
        return ref_found

    class Config:
        extra = "allow"


ComponentsParser.parser(raw_api=raw_api)
print(ComponentsParser.components_with_ref["schemas"])
print(ComponentsParser.components_without_ref["schemas"])
raw_inventory_item = raw_api.get("components").get("schemas").get("InventoryItem")
inventory_item = Schema(**raw_inventory_item)
