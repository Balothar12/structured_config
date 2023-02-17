
from typing import Any

class ValidationException(Exception):

    def __init__(self, value: Any, reason: str = "Unknown validation failure"):
        super().__init__(f"Validation failed for object '{str(value)}': {reason}")