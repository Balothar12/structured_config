
from typing import Any, Dict, List, Type, Protocol

class ConfigTypeCheckingFunction(Protocol):
    def __call__(self, key: str, parent_key: str, obj: Any, scalar: bool): ...
class ConvertedTypeCheckingFunction(Protocol):
    def __call__(self, key: str, parent_key: str, obj: Any): ...


class TypeConfig:

    _scalar_whitelist: List[Type] = [
        str, float, bool, int
    ]

    _object_whitelist: List[Type] = [
        List[Any], Dict[str, Any]
    ]

    @classmethod
    def allow_scalar_type(cls, new_type: Type): 
        cls._scalar_whitelist.append(new_type)

    @classmethod
    def disallow_scalar_type(cls, type: Type):
        if type in cls._scalar_whitelist:
            cls._scalar_whitelist.remove(type)

    @classmethod
    def change_scalar_whitelist(cls, whitelist: List[Type]):
        cls._scalar_whitelist = whitelist

    @classmethod
    def stringify_scalar_whitelist(cls, specific_types: List[Type] or None) -> List[str]:
        return [type.__name__ for type in TypeConfig._origins(list(set(cls._scalar_whitelist) & set(specific_types or cls._scalar_whitelist)))]
    
    @classmethod
    def stringify_object_whitelist(cls, specific_types: List[Type] or None) -> List[str]:
        return [type.__name__ for type in TypeConfig._origins(list(set(cls._object_whitelist) & set(specific_types or cls._object_whitelist)))]

    @classmethod
    def is_valid_scalar(cls, obj: Any, specific_types: List[Type] or None, allow_instance_of: bool = False):
        return cls._check_whitelist(obj=obj, whitelist=list(set(cls._scalar_whitelist) & set(specific_types or cls._scalar_whitelist)))
    
    @classmethod
    def is_valid_object(cls, obj: Any, specific_types: List[Type] or None, allow_instance_of: bool = False):
        return cls._check_whitelist(obj=obj, whitelist=list(set(cls._object_whitelist) & set(specific_types or cls._object_whitelist)))
    
    @staticmethod
    def no_config_checks() -> ConfigTypeCheckingFunction:
        return lambda key, parent_key, obj: None
        
    @staticmethod
    def no_converted_checks() -> ConvertedTypeCheckingFunction:
        return lambda key, parent_key, obj, scalar: None

    @staticmethod
    def _check_whitelist(obj: Any, whitelist: List[Type], allow_instance_of: bool) -> bool:
        return \
            type(obj) in TypeConfig._origins(whitelist) if not allow_instance_of else \
            any([isinstance(obj, type) for type in TypeConfig._origins(whitelist)])

    @staticmethod
    def _origins(types: List[Type]) -> List[Type]:
        return [getattr(type, "__origin__", type) for type in types]
