
from typing import TypeVar
from structured_config.validation.validation_exception import ValidationException
from structured_config.base.typedefs import ValidatorSourceType
from enum import Enum

ObjectType = TypeVar("ObjectType")

class ValidatorPhase(Enum):
    BeforeConversion = 0
    AfterConversion = 1
    NoValidation = 2

class ValidatorBase:

    def __init__(self, fail_reason: str = "Unknown validation failure"):
        self.fail_reason = fail_reason

    def __call__(self, data: ValidatorSourceType) -> ValidatorSourceType:
        if not self.validate(data=data):
            raise ValidationException(value=data, reason=self.fail_reason)
        else:
            return data

    def validate(self, data: ValidatorSourceType) -> bool:
        raise NotImplementedError()
