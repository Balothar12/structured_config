
from spec.config_value_base import ConfigValueBase
from conversion.converter_base import ConverterBase
from validation.validator_base import ValidatorBase, ValidatorPhase
from structured_config.validation.pass_all_validator import PassAllValidator
from conversion.no_op_converter import NoOpConverter
from typedefs import ConfigObjectType, ConversionTargetType
from spec.required_value_not_found_exception import RequiredValueNotFoundException
from spec.invalid_spec_exception import InvalidSpecException

class ScalarConfigValue(ConfigValueBase):
    """Scalar config value class
    
    Scalar config values represent single values in a config structure, e.g. strings
    or integers in a json file. The base objects read from the config file (string, int, 
    or boolean) can be converted to a target type (e.g. convert a date string to a date 
    object), and validated (e.g. validate an email or a file path). Validation can be
    performed before or after a value was converted. Scalar values can be optional and 
    have default values.

    Args:
        converter (ConverterBase): value converter, by default no conversion is applied
        validator (ValidatorBase): validator, by default all values are passed
        validator_phase (ValidatorPhase): when the validation should occur, by default before conversion
        required (bool): is the value required
        default (ConversionTargetType): default value, should be the same type as the converter output
    """

    def __init__(self,
                 converter: ConverterBase = NoOpConverter,
                 validator: ValidatorBase = PassAllValidator(),
                 validator_phase: ValidatorPhase = ValidatorPhase.BeforeConversion,
                 required: bool = True,
                 default: ConversionTargetType or None = None):
        
        self._converter: ConverterBase = converter
        self._validator: ValidatorBase = validator
        self._validator_phase: ValidatorPhase = validator_phase
        self._required: bool = required
        self._default: ConversionTargetType = default

        # validate the specification
        self._validate_spec()

    def _validate_spec(self):
        if self._default != None and self._required:
            raise InvalidSpecException(reason="Cannot have default values for required config values")

    def convert(self, input: ConfigObjectType or None, key: str, parent_key: str) -> ConversionTargetType:

        # check if the value exists
        if input == None:
            if self._required:
                raise RequiredValueNotFoundException(value_name=self.extend_key(aggregate=aggregate_key, key=key))
            else:
                return self._default

        # do we need to validate before we convert?
        if self._validator_phase == ValidatorPhase.BeforeConversion:
            input = self._validator(data=input)

        # perform data conversion        
        output: ConversionTargetType = self._converter(input)

        # do we need to validate after we convert?
        if (self._validator_phase == ValidatorPhase.AfterConversion):
            output = self._validator(data=output)

        # return final result
        return output

