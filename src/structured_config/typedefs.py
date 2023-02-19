from typing import TypeVar, Dict, List, Any

ConversionTargetType = TypeVar("ConversionTargetType")
ConversionSourceType = TypeVar("ConversionSourceType")

ValidatorSourceType = TypeVar("ValidatorSourceType")

ConfigObjectType = TypeVar("ConfigObjectType", Dict[str, Any], List[Any], str, int, float, bool)