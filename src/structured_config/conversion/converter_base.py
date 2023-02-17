
from structured_config.typedefs import ConversionSourceType, ConversionTargetType
from structured_config.conversion.conversion_type_exception import ConversionTypeException

class ConverterBase:

    def __call__(self, other: ConversionSourceType) -> ConversionTargetType:
        try:
            return self.convert(other=other)
        except:
            raise ConversionTypeException(type(other), self.typename())
        
    def typename(self) -> str:
        raise NotImplementedError()

    def convert(self, other: ConversionSourceType) -> ConversionTargetType:
        raise NotImplementedError()


