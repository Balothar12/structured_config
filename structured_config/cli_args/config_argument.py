
from dataclasses import dataclass
from typing import Any

from structured_config.cli_args.argparse_argument import ArgparseArgument

@dataclass
class ConfigArgument(ArgparseArgument):

    positional: bool
    short_name: str or None = None
    required: bool = True
    default: Any = None

    def __post_init__(self):
        self._positional = self.positional
        self._short_name = self.short_name
        self._required = self.required
        self._default = self.default

        super().__post_init__()
