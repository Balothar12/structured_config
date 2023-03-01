
from structured_config.type_checking.config_type_checker import ConfigTypeChecker
from structured_config.type_checking.converted_type_checker import ConvertedTypeChecker
from structured_config.type_checking.type_config import ConfigTypeCheckingFunction, ConvertedTypeCheckingFunction, TypeConfig

from typing import Any, Dict, List, Type, TypeVar

class RequireConfigType:

    @staticmethod
    def none() -> ConfigTypeCheckingFunction:
        return TypeConfig.no_config_checks()

    @staticmethod
    def scalar() -> ConfigTypeCheckingFunction:
        return ConfigTypeChecker(allow_instance_of=False)
    @staticmethod
    def string() -> ConfigTypeCheckingFunction:
        return ConfigTypeChecker(allow_instance_of=False, specific_types=[str])
    @staticmethod
    def integer() -> ConfigTypeCheckingFunction:
        return ConfigTypeChecker(allow_instance_of=False, specific_types=[int])
    @staticmethod
    def decimal() -> ConfigTypeCheckingFunction:
        return ConfigTypeChecker(allow_instance_of=False, specific_types=[float])
    @staticmethod
    def number() -> ConfigTypeCheckingFunction:
        return ConfigTypeChecker(allow_instance_of=False, specific_types=[int, float])
    @staticmethod
    def boolean() -> ConfigTypeCheckingFunction:
        return ConfigTypeChecker(allow_instance_of=False, specific_types=[bool])
    
    @staticmethod
    def object() -> ConfigTypeCheckingFunction:
        return ConfigTypeChecker(allow_instance_of=False, specific_types=[Dict[str, Any]])
    @staticmethod
    def list() -> ConfigTypeCheckingFunction:
        return ConfigTypeChecker(allow_instance_of=False, specific_types=[List[Any]])
    
    @staticmethod
    def from_type_list(types: List[Type]) -> ConfigTypeCheckingFunction:
        return ConfigTypeChecker(allow_instance_of=False, specific_types=types)
    
class RequireConvertedType:

    @staticmethod
    def none() -> ConvertedTypeCheckingFunction:
        return TypeConfig.no_converted_checks()
    
    @staticmethod
    def from_type_list(types: List[Type]) -> ConvertedTypeCheckingFunction:
        return ConvertedTypeChecker(allow_instance_of=False, any_of=types)