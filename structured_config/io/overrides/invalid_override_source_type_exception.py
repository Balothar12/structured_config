
from typing import Type


class InvalidOverrideSourceTypeException:

    def __init__(self, source_type: Type, expected_type: Type):
        super().__init__(f"Source has type '{source_type.__name__}', but should have type '{expected_type.__name__}'")