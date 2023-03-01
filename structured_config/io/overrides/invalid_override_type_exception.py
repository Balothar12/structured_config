
from typing import Type

class InvalidOverrideTypeException(Exception):

    def __init__(self, location: str, type: Type):
        super().__init__(f"Invalid override type at '{location}': must be 'str', 'int', 'float', or 'bool', but specified type is '{type.__name__}'")
