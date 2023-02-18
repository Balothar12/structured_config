
from structured_config.validation.validator_base import ValidatorBase, ValidatorSourceType
from typing import Type

class TypeCheckingValidator(ValidatorBase):
    """Type checking validator
    
    This validator checks if the type of the validated value matches the specified type. 
    If "allow_instance" is set to False (which is the default), the type must match using the
    "is" operator. Otherwise, "isinstance" is used. 

    Generally, type validation makes most sense to be perform on unconverted values: The reason
    for this is that in most other cases, you will be specifying the converter yourself, and 
    in general that means you should be sure about the type it returns. Therefore, using
    ValidationPhase.BeforeConversion probably makes most sense (this is the default as well).
    However, you may also validate converted types, e.g. if your converter may output values of
    different types depending on the input, and you only want to accept one kind. In this case,
    use ValidationPhase.AfterConversion.

    Note that for basic (i.e. non-typed, non-complex) scalar types, you can simply specify the
    "type" parameter to perform type checking. While this forces the checks to use "is" and does
    not allow "isinstance", this should not be required in this case since the only data you
    should expect are str/int/bool, lists, or dictionaries.

    Args:
        type (Type): expected data type
        allow_instance (bool): use "isinstance" for type checking (default is "False")
    """

    def __init__(self, type: Type, allow_instance: bool = False):
        self._type = type
        self._allow_instance = allow_instance

    def validate(self, data: ValidatorSourceType) -> bool:
        if self._allow_instance:
            return isinstance(data, self._type)
        else:
            return type(data) is self._type