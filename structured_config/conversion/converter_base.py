
from typing import Any, Type
from structured_config.base.typedefs import ConversionSourceType, ConversionTargetType
from structured_config.conversion.conversion_type_exception import ConversionTypeException

class ConverterBase:

    def __call__(self, other: ConversionSourceType, parent: str, current: str) -> ConversionTargetType:
        try:
            self.current: str = current
            self.parent: str = parent
            return self.convert(other=other)
        except ConversionTypeException as error:
            raise error
        except:
            raise ConversionTypeException(type(other), self.expected_type(), parent=parent, current=current)
        
    def expected_type(self) -> ConversionTargetType or None:
        return None

    def convert(self, other: ConversionSourceType) -> ConversionTargetType:
        raise NotImplementedError()


