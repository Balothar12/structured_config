
from structured_config.typedefs import ConversionSourceType, ConversionTargetType

from structured_config.conversion.converter_base import ConverterBase
from structured_config.conversion.invalid_object_type_exception import InvalidObjectTypeException

class TypeCastingConverter(ConverterBase):
    
    def __init__(self, to: ConversionTargetType):
        self.to: ConversionTargetType = to

    def typename(self) -> str:
        return self.to.__name__
    
    def type(self) -> str:
        return self.to

    def convert(self, other: ConversionSourceType) -> ConversionTargetType:
        # If "to" is "str", any type may be converted here, which is probably not desired.
        # To avoid just converting anything to strings, we disallow List, Dict, and Objects
        if self.to is str and (type(other) is list or type(other) is dict):
            raise InvalidObjectTypeException(source=type(other), target=self.to, current=self.current, parent=self.parent)
        return self.to(other)