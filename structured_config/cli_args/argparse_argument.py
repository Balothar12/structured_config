
import argparse
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Type
from enum import Enum

from structured_config.io.case_translation.case_translator_base import CaseTranslatorBase
from structured_config.io.case_translation.snake_case import SnakeCase

class ArgumentConfigException(Exception):
    def __init__(self, name: str, reason: str):
        super().__init__(f"Argument config for '{name}' is faulty: {reason}")

@dataclass
class ArgparseArgument:
    """Argparse argument config structure
    
    Generic base class for an argparse config argument. In order to restrict which fields should be initialized by subclasses, 
    not all of them will be available in the init function.

    Args:
        name (str): long name of the argument
        help (str): argument help string
        short_name (str): short name of the argument (only applicable if positional = False)
        positional (bool): should the argument be a positional argument (assumes optional argument if False)
        required (bool): determine whether the argument is required, if it's not a positional argument
        action (str): argparse action
        case (CaseTranslatorBase): a destination is not explicitly set, this argument can determine the case of
                                   the destination name (defaults to snake_case)
        dest (str or None): optional destination name, the case-translated long name will be used if this is not specified
    """
    name: str
    help: str
    _short_name: str or None = field(default=None, init=False)
    _positional: bool = field(default=True, init=False)
    _required: bool = field(default=True, init=False)
    _default: Any = field(default=None, init=False)
    _action: str = field(default="store", init=False)
    _case: CaseTranslatorBase = field(default=SnakeCase(), init=False)
    _dest: str or None = field(default=None, init=False)

    def __post_init__(self):
        if self._dest == None:
            self._dest = self._case.translate(key=self.name)

    def get_destination(self) -> str:
        return self._dest

    def apply(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        # determine name prefixes
        long_prefix, short_prefix = self._get_prefixes()

        # determine name options
        name_options: Tuple[str] or Tuple[str, str] = self._get_name_options(short_prefix=short_prefix, long_prefix=long_prefix)

        # determine keyword options
        keyword_options: Dict[str, Any] = self._get_keyword_options()

        # add argument
        parser.add_argument(*name_options, **keyword_options)

        return parser
        
    def _get_prefixes(self) -> Tuple[str, str]:
        return (
            "" if self._positional else "--",
            "" if self._positional else "-"
        )
    
    def _get_name_options(self, long_prefix: str, short_prefix: str) -> Tuple[str, str] or Tuple[str]:
        if self._positional:
            return (self.name,)
        elif self._short_name == None:
            return (f"{long_prefix}{self.name}",)
        else:
            return (f"{long_prefix}{self.name}", f"{short_prefix}{self._short_name}")
        
    def _get_keyword_options(self) -> Dict[str, Any]:
        options: Dict[str, Any] = {
            "action": self._action,
            "help": self.help,
        }

        if not self._positional:
            options["dest"] = self._dest
            options["required"] = self._required
            if not self._required:
                options["default"] = self._default

        return self.additional_keyword_options(options)
    
    def additional_keyword_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        return options
