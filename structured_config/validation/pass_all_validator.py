from structured_config.base.typedefs import ValidatorSourceType
from structured_config.validation.validator_base import ValidatorBase

class PassAllValidator(ValidatorBase):
    
    def __init__(self):
        super().__init__(fail_reason="Unknown validation failure")

    def validate(self, data: ValidatorSourceType) -> bool:
        # default validator passes everything
        return True