
import argparse
from dataclasses import dataclass
from typing import Any, Dict

from structured_config.cli_args.argparse_argument import ArgparseArgument
from structured_config.spec.config_value_base import ConfigValueBase

@dataclass 
class SchemaArgument(ArgparseArgument):

    def __post_init__(self):
        super().__post_init__()

    def pre_parse(self, config: ConfigValueBase):
        raise NotImplementedError()
    
    def post_parse(self, config: ConfigValueBase, args: argparse.Namespace) -> bool:
        raise NotImplementedError()