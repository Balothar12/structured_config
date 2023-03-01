
from typing import Any, List, Type

from structured_config.type_checking.type_config import TypeConfig


class ConfigTypeChecker:

    def __init__(self, allow_instance_of: bool, specific_types: List[Type] or None = None): 
        self._instance_of = allow_instance_of
        self._specific_types = specific_types

    def __call__(self, key: str, parent_key: str, obj: Any, scalar: bool):
        if not self._verify(obj=obj, scalar=scalar):
            # get the list of allowed typenames
            typenames: List[str] = \
                TypeConfig.stringify_scalar_whitelist(specific_types=self._specific_types) \
                    if scalar else \
                TypeConfig.stringify_object_whitelist(specific_types=self._specific_types)
            
            # show the error
            raise TypeError(f"Invalid config type: Object '{key}' under '{parent_key}' has "
                            f"invalid type '{type(obj).__name__}': expected one of "
                            f"'{typenames}'")
        
    def typename(self) -> str:
        if not self._specific_types or len(self._specific_types) == 0:
            return "any-type"
        elif len(self._specific_types) == 1:
            return self._specific_types[0].__name__
        else:
            return f"{[type.__name__ for type in self._specific_types]}"

    def _verify(self, obj: Any, scalar: bool) -> bool:
        return \
            TypeConfig.is_valid_scalar(obj=obj, allow_instance_of=self._instance_of, specific_types=self._specific_types) \
                if scalar else \
            TypeConfig.is_valid_object(obj=obj, allow_instance_of=self._instance_of, specific_types=self._specific_types)