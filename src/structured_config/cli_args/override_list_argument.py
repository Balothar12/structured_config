
from typing import Any, Dict, List
from dataclasses import dataclass, field

from structured_config.cli_args.argparse_argument import ArgparseArgument

@dataclass
class OverrideListArgument(ArgparseArgument):
    
    short_name: str or None = None
    required: bool = False
    default: List[List[str]] = field(default_factory=lambda: [])
    
    def __post_init__(self):
        self._positional = False
        self._short_name = self.short_name
        self._required = self.required
        self._default = self.default
        self._action = "append"

        super().__post_init__()

    def additional_keyword_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        options["nargs"] = 2
        return options