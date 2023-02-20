
from structured_config.typedefs import ValidatorSourceType
from structured_config.validation.validator_base import ValidatorBase

import re


class StrFormatValidator(ValidatorBase):

    def __init__(self, format: str, fullmatch: bool = True):
        self.format: str = format
        self.fullmatch: bool = fullmatch
        super().__init__()

    def validate(self, data: ValidatorSourceType) -> bool:
        if type(data) is not str:
            self.fail_reason = f"Data must be 'str' but is '{type(data).__name__}'"
            return False
        elif not re.fullmatch(pattern=self.format, string=data):
            self.fail_reason = f"String '{data}' does not match format '{self.format}"
            return False

        return True
    
    def _match(self, data: str) -> bool:
        return bool(re.fullmatch(pattern=self.format, string=data) if self.fullmatch else re.match(pattern=self.format, string=data))