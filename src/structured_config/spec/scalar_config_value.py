
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.io.schema.schema_writer_base import ValueDefinition
from structured_config.conversion.converter_base import ConverterBase
from structured_config.type_checking.config_type_checker import ConfigTypeChecker
from structured_config.type_checking.require_types import RequireConfigType
from structured_config.type_checking.type_config import ConfigTypeCheckingFunction, ConvertedTypeCheckingFunction, TypeConfig
from structured_config.validation.validator_base import ValidatorBase, ValidatorPhase
from structured_config.validation.pass_all_validator import PassAllValidator
from structured_config.conversion.no_op_converter import NoOpConverter
from structured_config.typedefs import ConfigObjectType, ConversionTargetType
from structured_config.spec.required_value_not_found_exception import RequiredValueNotFoundException
from structured_config.spec.invalid_spec_exception import InvalidSpecException

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from structured_config.io.schema.schema_writer_base import DefinitionBase

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
                 config_type_check: ConfigTypeCheckingFunction = RequireConfigType.scalar(),
                 converted_type_check: ConvertedTypeCheckingFunction = TypeConfig.no_converted_checks(),
                 converter: ConverterBase = NoOpConverter(),
                 validator: ValidatorBase = PassAllValidator(),
                 validator_phase: ValidatorPhase = ValidatorPhase.BeforeConversion,
                 required: bool = True,
                 default: ConversionTargetType or None = None):
        
        self._converter: ConverterBase = converter
        self._validator: ValidatorBase = validator
        self._validator_phase: ValidatorPhase = validator_phase
        self._required: bool = required
        self._default: ConversionTargetType = default
        self._config_type_check: ConfigTypeCheckingFunction = config_type_check
        self._converted_type_check: ConvertedTypeCheckingFunction = converted_type_check

        # validate the specification
        self._validate_spec()

    def _validate_spec(self):
        if self._default != None and self._required:
            raise InvalidSpecException(reason="Cannot have default values for required config values")
        
    def specify(self) -> 'DefinitionBase':
        return ValueDefinition(
            key_case=self.get_source_case(),
            type=self._converter.type(), 
            required=self._required, 
            default=self._default,
        )

    def convert(self, input: ConfigObjectType or None, key: str = "", parent_key: str = "") -> ConversionTargetType:

        # check if the value exists
        if input == None:
            if self._required:
                raise RequiredValueNotFoundException(value_name=self.extend_key(aggregate=parent_key, key=key))
            else:
                return self._default
            
        # check the config type
        self._config_type_check(key=key, parent_key=parent_key, obj=input, scalar=True)

        # do we need to validate before we convert?
        if self._validator_phase == ValidatorPhase.BeforeConversion:
            input = self._validator(data=input)

        # perform data conversion
        output: ConversionTargetType = self._converter(input, parent=parent_key, current=key)

        # check converted type
        self._converted_type_check(key=key, parent_key=parent_key, obj=output)

        # do we need to validate after we convert?
        if (self._validator_phase == ValidatorPhase.AfterConversion):
            output = self._validator(data=output)

        # return final result
        return output

