
from structured_config.typedefs import ConversionSourceType, ConversionTargetType

class ConversionTypeException(Exception):

    def __init__(self, source: ConversionSourceType, target: ConversionTargetType, parent: str, current: str):
        super().__init__(f"Conversion failure: Cannot convert object '{current}' under '{parent}' from "
                         f"type '{source.__name__}' to type '{getattr(target, '__name__', 'Unkown type')}'")
