
from conversion.converter_base import ConverterBase
from typedefs import ConversionSourceType, ConversionTargetType

class NoOpConverter(ConverterBase):

    def convert(self, other: ConversionSourceType) -> ConversionTargetType:
        return other