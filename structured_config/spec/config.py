
from structured_config.spec.entries.entry_base import EntryBase
from structured_config.spec.entries.object_requirements import ObjectRequirements
from structured_config.spec.scalar_config_value import ScalarConfigValue
from structured_config.spec.object_config_value import ObjectConfigValue
from structured_config.spec.list_config_value import ListConfigValue
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.type_checking.converted_type_checker import ConvertedTypeChecker
from structured_config.type_checking.require_types import RequireConfigType, RequireConvertedType
from structured_config.type_checking.type_config import ConfigTypeCheckingFunction, ConvertedTypeCheckingFunction, TypeConfig
from structured_config.validation.pass_all_validator import PassAllValidator
from structured_config.validation.validator_base import ValidatorBase, ValidatorPhase
from structured_config.validation.list_validator import ListValidator
from structured_config.conversion.no_op_converter import NoOpConverter
from structured_config.conversion.type_casting_converter import TypeCastingConverter
from structured_config.conversion.converter_base import ConverterBase
from structured_config.base.typedefs import ConversionSourceType, ConversionTargetType, ConfigObjectType, ScalarConfigTypeRequirements, ScalarConvertedTypeRequirements
from dataclasses import dataclass
from typing import List, Tuple, Protocol, TypeVar, get_type_hints, Dict, Any, Type, Callable

class Config:

    @staticmethod
    def scalar(validator: ValidatorBase = PassAllValidator(),
               type: ScalarConfigTypeRequirements = None,
               required: bool = True,
               default: ConfigObjectType or None = None) -> ScalarConfigValue:
        """Create a simple scalar value

        No type conversion, meaning that the type is used as-is from the config IO layer. However, one or more excepted types 
        may still be specified to indicate that the config file value should have that type. If any type is specified,
        it is checked during conversion. Otherwise, any type is allowed. Type-checking is done before any validators
        are applied. Valid "type" parameters include a single required, type a list of required types, or a custom type checking
        function. It is recommended to use the methods provided by "RequireConfigType", as these cover all supported config types.
        If you manually specify a type that isn't supported as a config object, without whitelisting it in "TypeConfig", type
        checking will always fail.

        Args:
            validator (ValidatorBase): optional validator
            type (ConfigTypeCheckingFunction or List[type] or None)
        """
        return ScalarConfigValue(
            validator=validator,
            validator_phase=ValidatorPhase.AfterConversion,
            converter=NoOpConverter(),
            required=required,
            default=default,
            config_type_check=RequireConfigType.make_type_checking_function(
                expected_types=type, 
                default=RequireConfigType.scalar(),
            )
        )

    @staticmethod
    def typed_scalar(cast_to: ConversionTargetType, 
                     type: ScalarConfigTypeRequirements = None,
                     validator: ValidatorBase = PassAllValidator(),
                     validate_when: ValidatorPhase = ValidatorPhase.BeforeConversion,
                     required: bool = True,
                     default: ConversionTargetType or None = None) -> ScalarConfigValue:
        """Create a typed scalar value

        Create a scalar value that is type-casted to the type specified in "cast_to". The "type" parameter may be used 
        to specify one or more optional required config types that are checked before any validators. The remaining parameters
        are the same as with the untyped scalar, with and added a validation phase parameter that indicates when validation
        should be performed (i.e. before or after type checking). The casted type is checked again after conversion to
        ensure that the returned type matches what is specified above.
        
        Args:
            cast_to (ConversionTargetType): value target type
            type (ScalarConfigTypeRequirements): expected config object type, optional
            validator (ValidatorBase): optional validator
            validate_when (ValidatorPhase): specify if the validation should happen before or after conversion
            required (bool): is the value required, defaults to "True"
            default (ConversionTargetType or None): optional default value, only applicable if "required" is "False"
        """
        return ScalarConfigValue(
            validator=validator,
            validator_phase=validate_when,
            converter=TypeCastingConverter(to=cast_to),
            required=required,
            default=default,
            config_type_check=RequireConfigType.make_type_checking_function(
                expected_types=type, 
                default=RequireConfigType.scalar(),
            ),
            converted_type_check=RequireConvertedType.from_type_list(types=[cast_to]),
        )
    
    @staticmethod
    def custom_scalar(converter: ConverterBase,
                      validator: ValidatorBase = PassAllValidator(),
                      validate_when: ValidatorPhase = ValidatorPhase.BeforeConversion,
                      type: ScalarConfigTypeRequirements = None,
                      converted_type: ScalarConvertedTypeRequirements = None,
                      required: bool = True,
                      default: ConversionTargetType or None = None) -> ScalarConfigValue:
        """Create a customized scalar value

        Here a custom conversion operator may be specified. This converter will be called with the config object value. If you
        want to validate the converted type before returning it, register one or more types using the converted_type parameter.
        
        Args:
            converter (ConverterBase): value converter
            type (ScalarConfigTypeRequirements): expected config object type, optional
            converted_type (ScalarConvertedTypeRequirements): expected converted type, optional
            validator (ValidatorBase): optional validator
            validate_when (ValidatorPhase): specify if the validation should happen before or after conversion
            required (bool): is the value required, defaults to "True"
            default (ConversionTargetType or None): optional default value, only applicable if "required" is "False"
        """
        return ScalarConfigValue(
            validator=validator,
            validator_phase=validate_when,
            converter=converter,
            required=required,
            default=default,
            config_type_check=RequireConfigType.make_type_checking_function(
                expected_types=type, 
                default=RequireConfigType.scalar(),
            ),
            converted_type_check=RequireConvertedType.make_type_checking_function(
                expected_types=converted_type, 
                default=RequireConvertedType.none(),
            ),
        )
    
    
    @staticmethod
    def typed_object(entries: List[EntryBase],
                     cast_to: ConversionTargetType,
                     requirements: ObjectRequirements or None = None) -> ObjectConfigValue:
        """Create a typed object value
        
        During the conversion process, the dictionary created by the entry list will be passed to the type's 
        constructor. In other words, if your target type supports a constructor that takes a dictionary with
        values as specified in the entry list, use this method for ease-of-use.

        Additionally, if your target type defines the static methods "required" and "defaults", these are used
        to define which scalar child-values are required, and what there default values will be if they aren't
        required. If your target class doesn't define those methods, and you can't/don't want to add them, it
        is also possible to specify the lists in a ObjectRequirements object. If you do not specify any 
        requirements, all entries are assumed to be required

        Args:
            entries (List[EntryBase]): list of children for this object
            cast_to (ConversionTargetType): config entry type, must be constructible from a dictionary
            requirements (ObjectRequirements): optional requirements object
        """
        
        return ObjectConfigValue(
            expected_children=dict([
                entry.create_value(object_type=cast_to, requirements=requirements) for entry in entries
            ]),
            converter=TypeCastingConverter(to=cast_to),
            converted_type_check=RequireConvertedType.from_type_list(types=[cast_to]),
        )

    @staticmethod
    def object(entries: List[EntryBase],
               converter: ConverterBase = NoOpConverter(),
               type: ScalarConvertedTypeRequirements = None,
               requirements: ObjectRequirements or None = None) -> ObjectConfigValue:
        """Create an object with a custom type converter
        
        If your target type does not support a dictionary constructor, or you want to perform some complex
        conversion operation, you need to use this method. You can still specify an output type to retrieve
        required and default values, or as above use a ObjectRequirements object.

        Args:
            entries (List[EntryBase]): list of children for this object
            converter (ConverterBase): type converter, takes a dictionary as its input
            type (ConversionTargetType): optional target type for required and default values
            requirements (ObjectRequirements): optional requirements object
        """
        
        return ObjectConfigValue(
            expected_children=dict([
                entry.create_value(object_type=type, requirements=requirements) for entry in entries
            ]),
            converter=converter,
            converted_type_check=RequireConvertedType.make_type_checking_function(
                expected_types=type,
                default=RequireConvertedType.none(),
            )
        )
    
    @staticmethod
    def typed_list(elements: ConfigValueBase,
                   cast_to: ConversionTargetType,
                   requirements: ListValidator = ListValidator()):
        """Create a list entry and convert the list to another type
        
        Each value in the list has the same definition. The values may be any config value: 
        list, object, or scalar. If you have requirements on the length of the list, specify
        a ListValidator with the appropriate arguments. If you have more complex list requirements,
        derive a subclass from ListValidator and override the "validate()" method. The target type's 
        constructor must be able to take a list as its sole input argument. If your conversion
        is more complex, or you need the list as-is, use the "list()" method instead.

        Args
            elements (ConfigValueBase): list element definition
            cast_to (ConversionTargetType): list-constructible target type for this config value
            requirements (ListValidator): list requirements

        """
        
        return ListConfigValue(
            child_definition=elements,
            list_requirements=requirements,
            converter=TypeCastingConverter(to=cast_to),
            converted_type_check=RequireConvertedType.from_type_list(types=[cast_to])
        )
    
    @staticmethod
    def list(elements: ConfigValueBase,
             requirements: ListValidator = ListValidator(),
             converter: ConverterBase = NoOpConverter(),
             type: ScalarConvertedTypeRequirements = None):
        """Create a list entry
        
        Each value in the list has the same definition. The values may be any config value: 
        list, object, or scalar. If you have requirements on the length of the list, specify
        a ListValidator with the appropriate arguments. If you have more complex list requirements,
        derive a subclass from ListValidator and override the "validate()" method. If you want to
        convert the resulting list into another type, specify an appropriate converter, or use 
        typed_list if your target type's constructor can directly a list.

        Args
            elements (ConfigValueBase): list element definition
            requirements (ListValidator): list requirements
            converter (ConverterBase): optional converter to convert the list into another type
        """
        
        return ListConfigValue(
            child_definition=elements,
            list_requirements=requirements,
            converter=converter,
            converted_type_check=RequireConvertedType.make_type_checking_function(
                expected_types=type,
                default=RequireConvertedType.none(),
            ),
        )
