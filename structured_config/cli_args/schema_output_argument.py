
import argparse
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict

from structured_config.cli_args.argparse_argument import ArgparseArgument
from structured_config.cli_args.schema_argument import SchemaArgument
from structured_config.io.schema.schema_writer_base import SchemaWriterBase
from structured_config.spec.config_value_base import ConfigValueBase

class SchemaOutputType(Enum):
    Screen = 0,
    File = 1

@dataclass 
class SchemaOutputArgument(SchemaArgument):

    writer: SchemaWriterBase
    output_type: SchemaOutputType = SchemaOutputType.Screen
    prefix: str = "Configuration schema:\n"
    short_name: str or None = None
    _config: ConfigValueBase or None = None

    def __post_init__(self):

        self._action = "store_true" if self.output_type == SchemaOutputType.Screen else "store"
        self._positional = False
        self._required = False
        self._default = False if self.output_type == SchemaOutputType.Screen else None

        super().__post_init__()

    def additional_keyword_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        return super().additional_keyword_options(options)
    
    def pre_parse(self, config: ConfigValueBase): ...
    
    def post_parse(self, config: ConfigValueBase, args: argparse.Namespace) -> bool:
        # check if the namespace has this schema option
        if getattr(args, self._dest, None) != None and self.output_type == SchemaOutputType.File:
            # yes: write the schema, and exit
            filepath: Path = Path(getattr(args, self._dest))
            if not filepath.parent.exists():
                filepath.parent.mkdir(parents=True)

            with open(file=filepath, mode="w") as file:
                file.write(self._write_schema(config=config))

            return False
    
        elif getattr(args, self._dest, False) and self.output_type == SchemaOutputType.Screen:
            # yes: print the schema, and exit
            print(f"{self.prefix}{self._write_schema(config=config)}")
            return False
        
        # no: keep executing
        return True
    
    def _write_schema(self, config: ConfigValueBase) -> str:
        return self.writer.define(config=config)