
from structured_config.io.case_translation.pascal_case import PascalCase
from structured_config.io.schema.json_like_writer import JsonLikeWriter
from structured_config.io.schema.yaml_like_writer import YamlLikeWriter
from structured_config.spec.config import Config, MakeScalarEntry, MakeListEntry, MakeCompositeEntry, MakeRequirements, ListValidator
from structured_config.io.reader.json_reader import JsonReader
from structured_config.io.reader.yaml_reader import YamlReader
from structured_config.io.case_translation.snake_case import SnakeCase

import json

def run():
    spec = Config.composite(
        entries=[
            MakeCompositeEntry.basic(
                name="person",
                entries=[
                    MakeScalarEntry.typed(name="first_name", type=str),
                    MakeScalarEntry.typed(name="last_name", type=str),
                    MakeScalarEntry.typed(name="age", type=int),
                    MakeScalarEntry.typed(name="gender", type=str),
                ],
                requirements=MakeRequirements.required([
                    "first_name", 
                    "last_name", 
                    "age",
                    "gender"
                ]),
            ),
            MakeListEntry.basic(
                name="addresses",
                elements=Config.composite(
                    entries=[
                        MakeScalarEntry.typed(name="street", type=str),
                        MakeScalarEntry.typed(name="number", type=str),
                        MakeScalarEntry.typed(name="secondary", type=str),
                        MakeScalarEntry.typed(name="zip", type=str),
                        MakeScalarEntry.typed(name="city", type=str),
                        MakeListEntry.basic(
                            name="occupants",
                            elements=Config.composite(
                                entries=[
                                    MakeScalarEntry.typed(name="first_name", type=str),
                                    MakeScalarEntry.typed(name="last_name", type=str),
                                ],
                                requirements=MakeRequirements.required([
                                    "first_name",
                                    "last_name",
                                ]),
                            ),
                        ),
                    ],
                    requirements=MakeRequirements.mixed(required=[
                        "street", 
                        "number", 
                        "zip",
                        "city"
                    ], defaults={
                        "secondary": None,
                    }),
                ),
            )
        ]
    )

    data = {
        "person": {
            "first_name": "Max",
            "last_name": "Mustermann",
            "age": 39,
            "gender": "male",
        },
        "addresses": [
            {
                "street": "Musterstr.",
                "number": "111c",
                "zip": 12345,
                "city": "Berlin",
                "occupants": [
                    {
                        "first_name": "Max",
                        "last_name": "Mustermann",
                    },
                    {
                        "first_name": "Maxine",
                        "last_name": "Musterfrau",
                    }
                ]
            }
        ]
    }

    # print(json.dumps(
    #     spec.convert(data),
    #     indent=2,
    #     ensure_ascii=True,
    # ))

    print(YamlLikeWriter(with_schema_case=True).define(config=spec))
    print(JsonLikeWriter(with_schema_case=True).define(config=spec))

    json_reader: JsonReader = JsonReader("test/person.json")
    print(json.dumps(
        spec
            .expect_source_case(source=SnakeCase())
            .require_target_case(target=SnakeCase())
            .convert(json_reader.read()),
        indent=2,
        ensure_ascii=True
    ))
    
    yaml_reader: YamlReader = YamlReader("test/person.yaml")
    print(json.dumps(
        spec
            .expect_source_case(source=PascalCase())
            .require_target_case(target=SnakeCase())
            .convert(yaml_reader.read()),
        indent=2,
        ensure_ascii=True
    ))

if __name__ == "__main__":
    run()
