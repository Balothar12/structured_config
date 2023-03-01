from typing import Type, TypeVar, Dict, List, Any

from structured_config.type_checking.type_config import ConfigTypeCheckingFunction, ConvertedTypeCheckingFunction

ConversionTargetType = TypeVar("ConversionTargetType")
ConversionSourceType = TypeVar("ConversionSourceType")

ValidatorSourceType = TypeVar("ValidatorSourceType")

ConfigObjectType = TypeVar("ConfigObjectType", Dict[str, Any], List[Any], str, int, float, bool)

ScalarConfigTypeRequirements = TypeVar("ScalarConfigTypeRequirements", ConfigTypeCheckingFunction, Type, List[Type], None)
ScalarConvertedTypeRequirements = TypeVar("ScalarConvertedTypeRequirements", ConvertedTypeCheckingFunction, Type, List[Type], None)
 