
from structured_config.typedefs import ConversionSourceType, ConversionTargetType

from structured_config.conversion.converter_base import ConverterBase

class TypeCastingConverter(ConverterBase):
    
    def __init__(self, to: ConversionTargetType):
        self.to: ConversionTargetType = to

    def typename(self) -> str:
        return self.to.name

    def convert(self, other: ConversionSourceType) -> ConversionTargetType:
        return self.to(other)