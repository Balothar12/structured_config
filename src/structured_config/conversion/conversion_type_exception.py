
from typedefs import ConversionSourceType, ConversionTargetType

class ConversionTypeException(Exception):

    def __init__(self, source: ConversionSourceType, target: ConversionTargetType):
        super().__init__(f"Conversion failure: Cannot convert from type '{source.name}' to type '{target.name}")