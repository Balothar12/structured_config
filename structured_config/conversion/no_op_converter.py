
from structured_config.conversion.converter_base import ConverterBase
from structured_config.base.typedefs import ConversionSourceType, ConversionTargetType
from typing import Type, Any

class NoOpConverter(ConverterBase):

    def __init__(self): ...

    def convert(self, other: ConversionSourceType) -> ConversionTargetType:
        return other