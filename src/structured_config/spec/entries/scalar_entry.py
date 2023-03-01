
from typing import Any, Tuple, Type, get_type_hints
from typing_extensions import Protocol
from structured_config.conversion.converter_base import ConverterBase
from structured_config.spec.config import Config
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.spec.entries.entry_base import EntryBase
from structured_config.spec.entries.object_requirements import ExtractRequirements, ObjectRequirements
from structured_config.spec.scalar_config_value import ScalarConfigValue

from structured_config.typedefs import ConversionTargetType, ScalarConfigTypeRequirements, ScalarConvertedTypeRequirements
from structured_config.validation.pass_all_validator import PassAllValidator
from structured_config.validation.validator_base import ValidatorBase, ValidatorPhase


class ObjectScalarConfigValueFactory(Protocol):
    def __call__(self, required: bool, default: ConversionTargetType or None) -> ScalarConfigValue: ...


class _ScalarEntry(EntryBase):
    """Create a scalar entry for an object config value
    """

    def __init__(self,
                 name: str,
                 create_config_value: ObjectScalarConfigValueFactory):
        self._name: str = name
        self._factory: ObjectScalarConfigValueFactory = create_config_value
        self._requirement_extractor: ExtractRequirements = ExtractRequirements(name=self._name)

    def create_value(self, 
                     object_type: ConversionTargetType or None,
                     requirements: ObjectRequirements or None) -> Tuple[str, ConfigValueBase]:
        """Create a (name, value) tuple for the defined scalar config value
        """
        return (self._name, self._factory(
            required=self._requirement_extractor.find_required(object_type=object_type, requirements=requirements), 
            default=self._requirement_extractor.find_default(object_type=object_type, requirements=requirements)
        ))
        
class ScalarEntry:
    
    @staticmethod
    def make(name: str,
              validator: ValidatorBase = PassAllValidator(),
              type: ScalarConfigTypeRequirements = None) -> '_ScalarEntry':
        """Create a simple scalar entry

        No type conversion, meaning that the type is used as-is from the config IO layer. However, one or more excepted types 
        may still be specified to indicate that the config file value should have that type. If any type is specified,
        it is checked during conversion. Otherwise, any type is allowed. Type-checking is done before any validators
        are applied. Valid "type" parameters include a single required type, a list of required types, or a custom type checking
        function. It is recommended to use the methods provided by "RequireConfigType", as these cover all supported config types.
        If you manually specify a type that isn't supported as a config object, without whitelisting it in "TypeConfig", type
        checking will always fail.

        Args:
            name (str): key of the value within its object parent
            validator (ValidatorBase): optional validator
        """
        return _ScalarEntry(
            name=name,
            create_config_value=lambda required, default: Config.scalar(
                validator=validator, 
                required=required, 
                default=default,
                type=type
            )
        )

    @staticmethod
    def typed(name: str,
              cast_to: ConversionTargetType, 
              type: ScalarConfigTypeRequirements = None,
              validator: ValidatorBase = PassAllValidator(),
              validate_when: ValidatorPhase = ValidatorPhase.BeforeConversion,) -> '_ScalarEntry':
        """Create a typed scalar entry

        Create a scalar value that is type-casted to the type specified in "cast_to". The "type" parameter may be used 
        to specify one or more optional required config types that are checked before any validators. The remaining parameters
        are the same as with the untyped scalar, with and added a validation phase parameter that indicates when validation
        should be performed (i.e. before or after type checking). The casted type is checked again after conversion to
        ensure that the returned type matches what is specified above.
        
        Args:
            name (str): key of the value within its object parent
            cast_to (ConversionTargetType): value target type
            type (ScalarConfigTypeRequirements): expected config object type, optional
            validator (ValidatorBase): optional validator
            validate_when (ValidatorPhase): specify if the validation should happen before or after conversion
        """
        return _ScalarEntry(
            name=name,
            create_config_value=lambda required, default: Config.typed_scalar(
                type=type,
                validator=validator, 
                validate_when=validate_when, 
                required=required, 
                default=default,
                cast_to=cast_to,
            )
        )
    
    @staticmethod
    def custom(name: str,
               converter: ConverterBase,
               validator: ValidatorBase = PassAllValidator(),
               validate_when: ValidatorPhase = ValidatorPhase.BeforeConversion,
               type: ScalarConfigTypeRequirements = None,
               converted_type: ScalarConvertedTypeRequirements = None) -> '_ScalarEntry':
        """Create a customized scalar entry

        Here a custom conversion operator may be specified. This converter will be called with the config object value. If you
        want to validate the converted type before returning it, register one or more types using the converted_type parameter.
        
        Args:
            converter (ConverterBase): value converter
            type (ScalarConfigTypeRequirements): expected config object type, optional
            converted_type (ScalarConvertedTypeRequirements): expected converted type, optional
            validator (ValidatorBase): optional validator
            validate_when (ValidatorPhase): specify if the validation should happen before or after conversion
        """
        return _ScalarEntry(
            name=name,
            create_config_value=lambda required, default: Config.custom_scalar(
                converter=converter,
                validator=validator,
                validate_when=validate_when,
                type=type,
                converted_type=converted_type, 
                required=required, 
                default=default
            )
        )