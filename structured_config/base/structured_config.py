
import argparse
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Type
from structured_config.cli_args.config_argument import ConfigArgument
from structured_config.cli_args.override_list_argument import OverrideListArgument
from structured_config.cli_args.schema_argument import SchemaArgument
from structured_config.cli_args.schema_output_argument import SchemaOutputArgument
from structured_config.io.case_translation.case_translator_base import CaseTranslatorBase
from structured_config.io.case_translation.no_translation import NoTranslation
from structured_config.io.case_translation.pascal_case import PascalCase
from structured_config.io.case_translation.snake_case import SnakeCase

from structured_config.io.overrides.mapper import Mapper
from structured_config.io.overrides.mapper_builder import MapperBuilder, MapperExtractorBuilder
from structured_config.io.reader.config_reader_base import ConfigReaderBase
from structured_config.io.reader.json_reader import JsonReader
from structured_config.io.reader.yaml_reader import YamlReader
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.base.typedefs import ConfigObjectType, ConversionTargetType

class ConfigFileArgumentType(Enum):
    Positional = 0
    Optional = 1

@dataclass
class ArgparseConfig:

    """Config for argparse setup
    
    Args:
        parser (argparse.ArgumentParser): application argument parser (arguments will be parsed when get_config() is called)
        use_for_overrides (bool): Use the override list in the program arguments to override config values .
                                  Custom override extraction should be done via the mapping_modifier in the OverrideConfig.
                                  This option is only for enabling or disabling the override list feature
        auto_setup (bool): automatically add structure_config setup options to argparse
        config_file_argument_type (ConfigFileArgumentType): should the config file argument be a positional or a (required) optional
        config_file_argument_name (str or None): config file argument name, will not be added if "None"
        config_file_argument_short_name (str or None): config file short argument name, will not be added if "None"
        overrides_list_name (str or None): override list argument name, will not be added if "None"
        overrides_list_short_name (str or None): override list short argument name, will not be added if "None"
    """
    parser: argparse.ArgumentParser

    use_for_overrides: bool

    auto_setup: bool = True

    config_file: ConfigArgument or None = ConfigArgument(
        name="config", 
        short_name="c", 
        required=True, 
        positional=True, 
        help="Configuration file location"
    )

    overrides_list: OverrideListArgument or None = OverrideListArgument(
        name="override",
        short_name=None,
        required=False,
        default=[],
        help="List of config overrides, specified using '--override <key> <value>'"
    )

    schema_options: List[SchemaArgument] = field(default_factory=lambda: [])

    def setup(self, config: ConfigValueBase) -> argparse.Namespace:
        if self.auto_setup:
            if self.config_file:
                self.config_file.apply(self.parser)
            if self.overrides_list:
                self.overrides_list.apply(self.parser)

            if len(self.schema_options) > 0:
                # required for screen schema output
                self.parser.formatter_class = argparse.RawDescriptionHelpFormatter

            for schema in self.schema_options:
                schema.pre_parse(config=config)
                schema.apply(self.parser)

        args: argparse.Namespace = self.parser.parse_args()
        # check post-parse status and exit if necessary
        if not self.post_parse(config=config, args=args):
            exit()
        return args
    
    def post_parse(self, config: ConfigValueBase, args: argparse.Namespace) -> bool:
        if self.auto_setup:
            # check schema options
            for schema in self.schema_options:
                if not schema.post_parse(config=config, args=args):
                    return False
        return True


    def override(self, override_config: 'OverrideConfig', arguments: argparse.Namespace):
        if self.use_for_overrides:
            override_config.mapper.build() \
                .from_argparse_keylist(
                        arguments=arguments, 
                        list_name=self.overrides_list.get_destination()) \
                    .all() \
                    .apply() \
                .apply()


@dataclass
class OverrideConfig:
    """Config for overrides

    Args:
        mapper (Mapper): override mapper config (will be populated automatically with argparse config list if specified)
        mapping_modifier (Callable[[MapperBuilder], MapperBuilder): add extractors using the mapper builder (use this if
                                                                    you don't want to specify the entire mapper)
    """
    mapper: Mapper = Mapper()
    mapping_modifier: Callable[[MapperBuilder], MapperBuilder] = lambda m: m

    def modify(self):
        self.mapping_modifier(self.mapper.build()).apply()

@dataclass
class FileConfig:
    """Input file config
    
    Args:
        file (str or None): optional config file location, not necessary if a valid argparse 
                            config exists to get the file location from that
        reader_override (Type or None): optional file reader override, if none is specified,
                                                    a reader will be chosen based on the file extension
        reader_extension_map (Dict[str, ConfigReaderBase): map file extension to reader classes that should be 
                                                           used to read the file
        reader_fallback (Type): Fallback reader if none of the specified extensions are recognized
        extension_source_case (Dict[str, CaseTranslatorBase]): source-case per extension (no translation if the 
                                                               extension wasn't found)
    """
    file: str or None = None
    reader_override: Type or None = None
    reader_extension_map: Dict[str, ConfigReaderBase] = field(default_factory=lambda: {
        ".json": JsonReader,
        ".yaml": YamlReader,
    })
    reader_fallback: Type = JsonReader
    extension_source_case: Dict[str, CaseTranslatorBase] = field(default_factory=lambda: {
        ".json": SnakeCase(),
        ".yaml": PascalCase(),
    })

    def read(self, file: str) -> ConfigObjectType:
        filepath: Path = Path(file)

        # select reader class
        reader_class: Type = None
        if self.reader_override != None:
            reader_class = self.reader_override
        if filepath.suffix in self.reader_extension_map:
            reader_class = self.reader_extension_map[filepath.suffix]
        else:
            reader_class = self.reader_fallback
        
        # try to read the config file
        reader: ConfigReaderBase = reader_class(file)
        return reader.read()
    
    def set_source_case(self, spec: ConfigValueBase, file: str) -> ConfigValueBase:
        return spec.expect_source_case(
            source=self.extension_source_case.get(Path(file).suffix, NoTranslation())
        )
        
class InvalidConfigSpecificationException(Exception):

    def __init__(self, reason: str):
        super().__init__(f"Config specification is invalid: {reason}")

class ConfigSpecification:

    def __init__(self, specification: ConfigValueBase):
        self.arg_config: ArgparseConfig or None = None
        self.override_config: OverrideConfig = OverrideConfig()
        self.file_config: FileConfig = FileConfig()
        self.specification = specification

    def with_argparse_config(self, arg_config: ArgparseConfig) -> 'ConfigSpecification':
        self.arg_config = arg_config
        return self
        
    def with_override_config(self, override_config: OverrideConfig) -> 'ConfigSpecification':
        self.override_config = override_config
        return self
    
    def with_file_config(self, file_config: FileConfig) -> 'ConfigSpecification':
        self.file_config = file_config
        return self
    
    def get_config(self) -> ConversionTargetType:
        self._validate_config()
        return self.specification.convert(input=self._prepare_config())
        
    def _prepare_config(self) -> ConfigObjectType:
        # initialize datan object
        data: ConfigObjectType = None
        file: str = None
        if self.arg_config:
            arguments: argparse.Namespace = self.arg_config.setup(config=self.specification)
            self.arg_config.override(override_config=self.override_config, arguments=arguments)

            # read data from argparse if possible
            file = getattr(
                    arguments, 
                    self.arg_config.config_file.get_destination() if self.arg_config.config_file else "_NOT_AN_ATTRIBUTE_", 
                    self.file_config.file
                )
            
        else:
            # directly read data using the file config
            file = self.file_config.file

        # read data and set expected source case
        data = self.file_config.read(file=file)
        self.file_config.set_source_case(spec=self.specification, file=file)

        # modify mapper and apply overrides
        self.override_config.modify()
        return self.override_config.mapper \
            .with_source_case(source_case=self.specification.get_source_case()) \
            .apply(to=data)



    def _validate_config(self):
        # check config file location
        if self.file_config.file == None and (self.arg_config == None or self.arg_config.config_file == None):
            raise InvalidConfigSpecificationException(reason="No config file provided, and file cannot be read from argparse")  

        # overrides_list_name must be specified in argparse if it's meant to be used for overrides
        if self.arg_config != None and self.arg_config.use_for_overrides and self.arg_config.overrides_list == None:
            raise InvalidConfigSpecificationException(reason="Override list name must be specified if it should be used")  
