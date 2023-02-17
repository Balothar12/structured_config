
from structured_config.conversion.converter_base import ConverterBase
from structured_config.conversion.invalid_object_type_exception import InvalidObjectTypeException
from structured_config.typedefs import ConversionSourceType, ConversionTargetType
from typing import Type, Any

class NoOpConverter(ConverterBase):

    def __init__(self, expected_type: Type or None = None):
        self._expected = expected_type

    def convert(self, other: ConversionSourceType) -> ConversionTargetType:
        if self._expected != None and type(other) is not self._expected:
            raise InvalidObjectTypeException(source=type(other), target=self._expected, current=self.current, parent=self.parent)
        return other
    
    def typename(self) -> str:
        if self._expected != None:
            return self._expected.__name__
        else:
            return "any-type"
        
    def type(self) -> ConversionTargetType:
        return self._expected