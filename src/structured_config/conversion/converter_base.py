
from structured_config.typedefs import ConversionSourceType, ConversionTargetType
from structured_config.conversion.conversion_type_exception import ConversionTypeException
from structured_config.conversion.invalid_object_type_exception import InvalidObjectTypeException

class ConverterBase:

    def __call__(self, other: ConversionSourceType, parent: str, current: str) -> ConversionTargetType:
        try:
            self.current: str = current
            self.parent: str = parent
            return self.convert(other=other)
        except Exception as error:
            if isinstance(error, ConversionTypeException) or isinstance(error, InvalidObjectTypeException):
                raise error
            else:
                raise ConversionTypeException(type(other), self.type(), parent=parent, current=current)
        
    def typename(self) -> str:
        raise NotImplementedError()
    
    def type(self) -> ConversionTargetType:
        raise NotImplementedError()

    def convert(self, other: ConversionSourceType) -> ConversionTargetType:
        raise NotImplementedError()


