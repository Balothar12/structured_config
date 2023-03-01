
import argparse
from structured_config.cli_args.schema_output_argument import SchemaOutputArgument, SchemaOutputType
from structured_config.io.case_translation.pascal_case import PascalCase
from structured_config.io.overrides.argparse_extractor import ArgparseOverrides
from structured_config.io.overrides.assignment import Assignment, Override
from structured_config.io.overrides.mapper import Mapper
from structured_config.io.schema.json_like_writer import JsonLikeWriter
from structured_config.io.schema.yaml_like_writer import YamlLikeWriter
from structured_config.io.reader.json_reader import JsonReader
from structured_config.io.reader.yaml_reader import YamlReader
from structured_config.io.case_translation.snake_case import SnakeCase


from typing import List
import json
from structured_config.spec.config import Config
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.spec.entries.list_entry import ListEntry
from structured_config.spec.entries.object_entry import ObjectEntry
from structured_config.spec.entries.object_requirements import MakeRequirements
from structured_config.spec.entries.scalar_entry import ScalarEntry

from structured_config.structured_config import ArgparseConfig, ConfigSpecification
from structured_config.validation.str_format_validator import StrFormatValidator

from structured_config.type_checking.require_types import RequireConfigType, RequireConvertedType

def run():
    spec = Config.object(
        entries=[
            ObjectEntry.make(
                name="person",
                entries=[
                    ScalarEntry.typed(name="first_name", type=str),
                    ScalarEntry.typed(name="last_name", type=str),
                    ScalarEntry.typed(name="age", type=int),
                    ScalarEntry.typed(name="gender", type=str),
                ],
                requirements=MakeRequirements.required([
                    "first_name", 
                    "last_name", 
                    "age",
                    "gender"
                ]),
            ),
            ListEntry.make(
                name="addresses",
                elements=Config.object(
                    entries=[
                        ScalarEntry.typed(name="street", type=str, cast_to=str),
                        ScalarEntry.typed(name="number", type=str, cast_to=str),
                        ScalarEntry.typed(name="secondary", type=str, cast_to=str),
                        ScalarEntry.typed(name="zip", type=str, cast_to=str),
                        ScalarEntry.typed(name="city", type=str, cast_to=str),
                        ListEntry.make(
                            name="occupants",
                            elements=Config.object(
                                entries=[
                                    ScalarEntry.typed(name="first_name", type=str, cast_to=str),
                                    ScalarEntry.typed(name="last_name", type=str, cast_to=str),
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

    override_mapper: Mapper = Mapper()                                              \
        .direct(key="person.first_name", value="Maximilian")                        \
        .direct(key="addresses.[0].occupants.[0].first_name", value="Maximilian")   \
        .direct(key="addresses.[0].occupants.+.first_name", value="Maxine")         \
        .direct(key="addresses.[0].occupants.[1].last_name", value="Musterfrau")    \
        .direct(key="addresses.+.street", value="Musterstr")                        \
        .direct(key="addresses.[1].number", value="15a")                            \
        .direct(key="addresses.[1].secondary", value="Basement")                    \
        .direct(key="addresses.[1].zip", value="12345")                             \
        .direct(key="addresses.[1].city", value="Berlin")                           \
        .direct(key="addresses.[1].occupants.+.first_name", value="Maxi")           \
        .direct(key="addresses.[1].occupants.[0].last_name", value="Mustersohn")
    
    parser: argparse.ArgumentParser = argparse.ArgumentParser("Testing overrides")

    parser.add_argument("--config", action="append", nargs=2, type=str)
    parser.add_argument("--person-first-name")
    parser.add_argument("--person-last-name")

    args = parser.parse_args([
        "--config", "person.age", "34",
        "--config", "person.gender", "female",
        "--person-first-name", "John",
        "--person-last-name", "Doe",
    ])

    overrides1 = ArgparseOverrides.from_list(list_name="config", arguments=args)
    overrides2 = ArgparseOverrides.fixed(map={
        "person_first_name": "person.first_name", 
        "person_last_name": "person.last_name"
    }, arguments=args)

    print(overrides1.available_keys())
    print(overrides1.all_available())
    print(overrides2.available_keys())
    print(overrides2.all_available())

    # print(json.dumps(
    #     spec.convert(data),
    #     indent=2,
    #     ensure_ascii=True,
    # ))

    print(YamlLikeWriter(with_schema_case=True).define(config=spec))
    print(JsonLikeWriter(with_schema_case=True).define(config=spec))

    json_reader: JsonReader = JsonReader("test/person.json")
    print("From JSON:")
    print(json.dumps(
        spec
            .expect_source_case(source=SnakeCase())
            .require_target_case(target=SnakeCase())
            .convert(override_mapper
                        .with_source_case(source_case=SnakeCase())
                        .apply(to=json_reader.read())
                    ),
        indent=2,
        ensure_ascii=True
    ))
    print("------------")
    
    yaml_reader: YamlReader = YamlReader("test/person.yaml")
    print("From YAML:")
    print(json.dumps(
        spec
            .expect_source_case(source=PascalCase())
            .require_target_case(target=SnakeCase())
            .convert(override_mapper
                        .with_source_case(source_case=PascalCase())
                        .apply(to=yaml_reader.read())
                    ),
        indent=2,
        ensure_ascii=True
    ))


def run2():

    config = ConfigSpecification(specification=Config.object(
        entries=[
            ObjectEntry.make(
                name="person",
                entries=[
                    ScalarEntry.typed(name="first_name", cast_to=str, type=RequireConfigType.string()),
                    ScalarEntry.typed(name="last_name", cast_to=str, type=RequireConfigType.string()),
                    ScalarEntry.typed(name="age", cast_to=float, type=RequireConfigType.number()),
                    ScalarEntry.typed(name="gender", cast_to=str, type=RequireConfigType.string()),
                ],
                requirements=MakeRequirements.required([
                    "first_name", 
                    "last_name", 
                    "age",
                    "gender"
                ]),
            ),
            ListEntry.make(
                name="addresses",
                elements=Config.object(
                    entries=[
                        ScalarEntry.typed(name="street", cast_to=str, type=RequireConfigType.string()),
                        ScalarEntry.typed(name="number", cast_to=str, type=RequireConfigType.string()),
                        ScalarEntry.typed(name="secondary", cast_to=str, type=RequireConfigType.string()),
                        ScalarEntry.typed(name="zip", cast_to=str, type=RequireConfigType.string(), validator=StrFormatValidator(format='[0-9]{5}')),
                        ScalarEntry.typed(name="city", cast_to=str, type=RequireConfigType.string()),
                        ListEntry.make(
                            name="occupants",
                            elements=Config.object(
                                entries=[
                                    ScalarEntry.typed(name="first_name", cast_to=str, type=RequireConfigType.string()),
                                    ScalarEntry.typed(name="last_name", cast_to=str, type=RequireConfigType.string()),
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
        ],
        requirements=MakeRequirements.mixed(
            required=["person"],
            defaults={"addresses": [{"valid": False}]}
        )
    ).require_target_case(target=SnakeCase())) \
    .with_argparse_config(arg_config=ArgparseConfig(
        parser=argparse.ArgumentParser("Config specification test"),
        auto_setup=True,
        use_for_overrides=True,
        schema_options=[
            SchemaOutputArgument(
                name="jschema", short_name="s",
                help="Describe the JSON config schema by printing it to the screen",
                output_type=SchemaOutputType.Screen,
                writer=JsonLikeWriter()
            ),
            SchemaOutputArgument(
                name="jschema-out", short_name="so",
                help="Describe the JSON config schema by writing it to the specified file",
                output_type=SchemaOutputType.File,
                writer=JsonLikeWriter()
            ),
            SchemaOutputArgument(
                name="yschema", short_name="s",
                help="Describe the YAML config schema by printing it to the screen",
                output_type=SchemaOutputType.Screen,
                writer=YamlLikeWriter(with_schema_case=True)
            ),
            SchemaOutputArgument(
                name="yschema-out", short_name="so",
                help="Describe the YAML config schema by writing it to the specified file",
                output_type=SchemaOutputType.File,
                writer=YamlLikeWriter(with_schema_case=True)
            ),
        ]
    )) \
    .get_config()


    print(json.dumps(
        config,
        indent=2,
        ensure_ascii=True
    ))

if __name__ == "__main__":
    run2()
