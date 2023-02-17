
from structured_config.typedefs import ConversionSourceType, ConversionTargetType


class InvalidObjectTypeException(Exception):

    def __init__(self, source: ConversionSourceType, target: ConversionTargetType, parent: str, current: str):
        super().__init__(f"Invalid object type: Expected '{current}' under '{parent}' to have type '{target.__name__}', but it has type '{source.__name__}'")