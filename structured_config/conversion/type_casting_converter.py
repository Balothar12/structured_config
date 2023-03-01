
from typing import Type
from structured_config.base.typedefs import ConversionSourceType, ConversionTargetType

from structured_config.conversion.converter_base import ConverterBase

class TypeCastingConverter(ConverterBase):
    
    def __init__(self, to: ConversionTargetType):
        self.to: ConversionTargetType = to

    def convert(self, other: ConversionSourceType) -> ConversionTargetType:
        return self.to(other)
    
    def expected_type(self) -> ConversionTargetType or None:
        return self.to