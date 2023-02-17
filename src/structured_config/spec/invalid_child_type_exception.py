
from structured_config.typedefs import ConfigObjectType

class InvalidChildTypeException(Exception):

    def __init__(self, child_type: ConfigObjectType, excepted_type: ConfigObjectType, child_key: str, parent_key: str):
        super().__init__(f"Child '{child_key}' under '{parent_key}' was expected to have type '{excepted_type.name}', "
                         f"but has type '{child_type.name}'")