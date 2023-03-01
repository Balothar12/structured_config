
from structured_config.type_checking.config_type_checker import ConfigTypeChecker
from structured_config.type_checking.converted_type_checker import ConvertedTypeChecker
from structured_config.type_checking.type_config import ConfigTypeCheckingFunction, ConvertedTypeCheckingFunction, TypeConfig

from typing import Any, Dict, List, Type, TypeVar

from structured_config.typedefs import ScalarConfigTypeRequirements, ScalarConvertedTypeRequirements

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
    
    @staticmethod
    def make_type_checking_function(expected_types: ScalarConfigTypeRequirements, 
                                    default: ConfigTypeCheckingFunction) -> ConfigTypeCheckingFunction:
        if type(expected_types) is list:
            return RequireConfigType.from_type_list(types=expected_types)
        elif callable(expected_types):
            return expected_types  
        elif expected_types:
            return RequireConfigType.from_type_list(types=[expected_types])
        else:
            return default
    
class RequireConvertedType:

    @staticmethod
    def none() -> ConvertedTypeCheckingFunction:
        return TypeConfig.no_converted_checks()
    
    @staticmethod
    def from_type_list(types: List[Type]) -> ConvertedTypeCheckingFunction:
        return ConvertedTypeChecker(allow_instance_of=False, any_of=types)

    @staticmethod
    def make_type_checking_function(expected_types: ScalarConvertedTypeRequirements, 
                                    default: ConvertedTypeCheckingFunction) -> ConvertedTypeCheckingFunction:
        if type(expected_types) is list:
            return RequireConvertedType.from_type_list(types=expected_types)
        elif callable(expected_types):
            return expected_types  
        elif expected_types:
            return RequireConvertedType.from_type_list(types=[expected_types])
        else:
            return default