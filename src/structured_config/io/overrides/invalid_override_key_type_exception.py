
from typing import Any, Type


class InvalidOverrideKeyTypeException(Exception):

    def __init__(self, key: Any, type: Type, expected: Type):
        super().__init__(f"Expected key '{str(key)}' to have type '{type.__name__}', but got '{expected.__name__}'")