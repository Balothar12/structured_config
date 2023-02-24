
from typing import Any, List, Type


class ConvertedTypeChecker:

    def __init__(self, any_of: List[Type], allow_instance_of: bool):
        self._any_of: Type = any_of
        self._instance_of: bool = allow_instance_of

    def __call__(self, key: str, parent_key: str, obj: Any):
        if not self._verify(obj=obj):
            raise TypeError(f"Invalid converted type: Object '{key}' under '{parent_key}' has "
                            f"invalid type '{type(obj).__name__}': expected one of '{self._stringify_types()}'")
    
    def _verify(self, obj: Any) -> bool:
        return \
            any([isinstance(obj, one_type) for one_type in self._any_of]) \
                if self._instance_of else \
            any([type(obj) is one_type for one_type in self._any_of])
    
    def _stringify_types(self) -> List[str]:
        return [self._stringify_one_type(type=one_type) for one_type in self._any_of]
    
    def _stringify_one_type(self, type: Type) -> str:
        if hasattr(type, "__origin__"):
            return getattr(getattr(type, "__origin__"), "__name__", str(type))
        else:
            return getattr(type, "__name__", str(type))