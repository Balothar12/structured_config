
from structured_config.spec.scalar_config_value import ScalarConfigValue
from structured_config.spec.composite_config_value import CompositeConfigValue
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
from structured_config.typedefs import ConversionSourceType, ConversionTargetType, ConfigObjectType
from dataclasses import dataclass
from typing import List, Tuple, Protocol, TypeVar, get_type_hints, Dict, Any, Type, Callable

ScalarConfigTypeRequirements = TypeVar("ScalarConfigTypeRequirements", ConfigTypeCheckingFunction, Type, List[Type], None)
ScalarConvertedTypeRequirements = TypeVar("ScalarConvertedTypeRequirements", ConfigTypeCheckingFunction, Type, List[Type], None)

class CompositeScalarConfigValueFactory(Protocol):
    def __call__(self, required: bool, default: ConversionTargetType or None) -> ScalarConfigValue: ...

@dataclass
class _CompositeRequirements:
    required_list: List[str]
    defaults_dict: Dict[str, ConversionTargetType or None]

    def __post_init__(self):
        self.required: Callable[[], List[str]] = self._get_required
        self.defaults: Callable[[], Dict[str, ConversionTargetType]] = self._get_defaults

    def _get_required(self) -> List[str]:
        return self.required_list
    def _get_defaults(self) -> Dict[str, ConversionTargetType or None]:
        return self.defaults_dict

class MakeRequirements:
    
    @staticmethod
    def required(required: List[str]):
        return _CompositeRequirements(required_list=required, defaults_dict={})
    
    @staticmethod
    def optional(defaults: Dict[str, ConversionTargetType or None]):
        return _CompositeRequirements(required_list=[], defaults_dict=defaults)
    
    @staticmethod
    def mixed(required: List[str], defaults: Dict[str, ConversionTargetType or None]):
        return _CompositeRequirements(required_list=required, defaults_dict=defaults)

class CompositeEntry:
    """Base class for composite entries

    Subclasses implement the create_value function, which will return a (name, value) tuple
    with the defined config value. The "composite_type" and "requirements" parameters are 
    required only for scalar entries.
    """

    def create_value(self, 
                     composite_type: ConversionTargetType or None, 
                     requirements: _CompositeRequirements or None) -> Tuple[str, ConfigValueBase]:
        """Create the config value

        This function will be overridden in the base classes. composite_type and requirements are
        only relevant for scalar entries. If the composite_type defines required() and defaults() 
        static methods, returning a List[str] and Dict[str, Type], respectively, they will be used to
        determine if a key is required, and the default value of that key. If either of these functions 
        are not defined, the requirements object will be used to check any user-defined requirements.
        If that object is not specified, the value is treated as required by default.
        """
        raise NotImplementedError()

    @staticmethod
    def requirements(self, required: List[str], defaults: Dict[str, ConversionTargetType or None]) -> object:
        return _CompositeRequirements(required_list=required, defaults_dict=defaults)
    
class MakeCompositeEntry(CompositeEntry):
    """Create a composite entry for a composite config value"""

    def __init__(self,
                 name: str,
                 entries: List[CompositeEntry],
                 converter: ConverterBase,
                 type: ScalarConvertedTypeRequirements,
                 requirements: _CompositeRequirements or None):
        self._name: str = name
        self._entries: List[CompositeEntry] = entries
        self._converter: ConverterBase = converter
        self._type: ScalarConvertedTypeRequirements = type
        self._requirements: _CompositeRequirements or None = requirements
        
        
    def create_value(self, 
                     composite_type: ConversionTargetType or None, 
                     requirements: _CompositeRequirements or None) -> Tuple[str, ConfigValueBase]:
        """Create a (name, value) tuple for the defined composite config value
        """
        return (self._name,
                CompositeConfigValue(
                    expected_children=dict([
                        entry.create_value(composite_type=self._type, requirements=self._requirements) for entry in self._entries
                    ]),
                    converter=self._converter,
                    converted_type_check=Config._make_converted_type_checking_function(
                        expected_types=self._type,
                        default=RequireConvertedType.none(),
                    ),
                )
            )
    
    @staticmethod
    def typed(name: str,
              entries: List[CompositeEntry],
              cast_to: ConversionTargetType,
              requirements: _CompositeRequirements or None = None) -> 'MakeCompositeEntry':
        """Create a typed list entry for a composite value

        See the documentation of "Config.typed_composite()" for details on typed composite config entries.
            
        Args
            name (str): key of the entry in the composite
            entries (List[CompositeEntry]): list of children for this composite
            type (ConversionTargetType): config entry type, must be constructible from a dictionary
            requirements (_CompositeRequirements): optional requirements object
        """
        return MakeCompositeEntry(
            name=name,
            entries=entries,
            converter=TypeCastingConverter(to=type),
            type=cast_to,
            requirements=requirements,
        )
    
    @staticmethod
    def make(name: str,
             entries: List[CompositeEntry],
             converter: ConverterBase = NoOpConverter(),
             type: ScalarConvertedTypeRequirements = None,
             requirements: _CompositeRequirements or None = None) -> 'MakeCompositeEntry':
        """Create a composite entry for a composite value

        See the documentation of "Config.composite()" for details on composite config entries.
        
        Args
            name (str): key of the list in the composite
            entries (List[CompositeEntry]): list of children for this composite
            converter (ConverterBase): type converter, takes a dictionary as its input
            type (ConversionTargetType): optional target type for required and default values
            requirements (_CompositeRequirements): optional requirements object
        """
        return MakeCompositeEntry(
            name=name,
            entries=entries,
            converter=converter,
            type=type,
            requirements=requirements,
        )
    
class MakeListEntry(CompositeEntry):
    """Create a list entry for a composite config value"""

    def __init__(self,
                 name: str,
                 elements: ConfigValueBase,
                 converter: ConverterBase,
                 type: ScalarConvertedTypeRequirements,
                 requirements: ListValidator):
        self._name: str = name
        self._elements: ConfigValueBase = elements
        self._converter: ConverterBase = converter
        self._type: ScalarConvertedTypeRequirements = type
        self._requirements: ListValidator = requirements
        
    def create_value(self, 
                     composite_type: ConversionTargetType or None, 
                     requirements: _CompositeRequirements or None) -> Tuple[str, ConfigValueBase]:
        """Create a (name, value) tuple for the defined list config value
        """
        return (self._name, ListConfigValue(
            child_definition=self._elements,
            list_requirements=self._requirements,
            converter=self._converter,
            converted_type_check=Config._make_converted_type_checking_function(
                expected_types=self._type,
                default=RequireConvertedType.none(),
            )
        ))

    @staticmethod
    def typed(name: str,
              elements: ConfigValueBase,
              cast_to: ConversionTargetType,
              requirements: ListValidator = ListValidator()) -> 'MakeListEntry':
        """Create a typed list entry for a composite value

        See the documentation of "Config.typed_list()" for details on typed list config entries.
            
        Args
            name (str): key of the list in the composite
            elements (ConfigValueBase): list element definition
            cast_to (ConversionTargetType): list-constructible target type for this config value
            requirements (ListValidator): list requirements
        """
        return MakeListEntry(
            name=name,
            elements=elements,
            converter=TypeCastingConverter(to=cast_to),
            requirements=requirements,
            type=cast_to,
        )
    
    @staticmethod
    def make(name: str,
             elements: ConfigValueBase,
             requirements: ListValidator = ListValidator(),
             converter: ConverterBase = NoOpConverter(),
             type: ScalarConvertedTypeRequirements = None) -> 'MakeListEntry':
        """Create a list entry for a composite value

        See the documentation of "Config.list()" for details on list config entries.
        
        Args
            name (str): key of the list in the composite
            elements (ConfigValueBase): list element definition
            requirements (ListValidator): list requirements
            converter (ConverterBase): optional converter to convert the list into another type
        """
        return MakeListEntry(
            name=name,
            elements=elements,
            converter=converter,
            requirements=requirements,
            type=type,
        )
    
class ScalarEntry(CompositeEntry):
    """Create a scalar entry for a composite config value
    """

    def __init__(self,
                 name: str,
                 create_config_value: CompositeScalarConfigValueFactory):
        self._name: str = name
        self._factory: CompositeScalarConfigValueFactory = create_config_value

    def create_value(self, 
                     composite_type: ConversionTargetType or None, 
                     requirements: _CompositeRequirements or None) -> Tuple[str, ConfigValueBase]:
        """Create a (name, value) tuple for the defined scalar config value
        """
        return (self._name, self._factory(
            required=self._find_required(composite_type=composite_type, requirements=requirements), 
            default=self._find_default(composite_type=composite_type, requirements=requirements)
        ))
    
    def _get_required_method(self, 
                             composite_type: ConversionTargetType or None, 
                             requirements: _CompositeRequirements or None) -> Any:
        return self._get_method_with_fallback(main=composite_type, 
                                              fallback=requirements, 
                                              method="required",
                                              expected_return_type=list)
    
    def _get_defaults_method(self, 
                             composite_type: ConversionTargetType or None, 
                             requirements: _CompositeRequirements or None) -> Any:
        return self._get_method_with_fallback(main=composite_type, 
                                              fallback=requirements, 
                                              method="defaults",
                                              expected_return_type=dict)
    
    def _get_method_with_fallback(self, 
                                  main: Any, 
                                  fallback: Any,
                                  method: str,
                                  expected_return_type: Type) -> Any:
        """Try to get the specified method with the specified return type

        Try the main object first, then try the fallback object. If neither has a matching attribute, 
        return "None", otherwise return the callable attribute.
        """
        method_attr: Any = None
        if main != None:
            attr = getattr(main, method, None)
            if attr != None and callable(attr) and get_type_hints(attr)["return"].__origin__ is expected_return_type:
                method_attr = attr
        if method_attr == None and fallback != None:
            attr = getattr(fallback, method, None)
            if attr != None and callable(attr) and get_type_hints(attr)["return"].__origin__ is expected_return_type:
                method_attr = attr
        return method_attr
    
    def _find_required(self, 
                       composite_type: ConversionTargetType or None, 
                       requirements: _CompositeRequirements or None) -> bool:
        # get the "required" method
        required_method = self._get_required_method(composite_type=composite_type, requirements=requirements)
        # verify the method
        if callable(required_method) and get_type_hints(required_method)["return"].__origin__ is list:
            # get the default value
            return self._name in required_method()
        else:
            # values are required by default, because the assumption is that if a class
            # doesn't define the "required" method, it won't define the "defaults" method
            # either
            return True

    def _find_default(self, 
                       composite_type: ConversionTargetType or None, 
                       requirements: _CompositeRequirements or None) -> ConversionTargetType:
        # get the "defaults" method
        defaults_method = self._get_defaults_method(composite_type=composite_type, requirements=requirements)
        # verify the method
        if callable(defaults_method) and get_type_hints(defaults_method)["return"].__origin__ is dict:
            # get the default value
            return defaults_method().get(self._name, None)
        else:
            # we cannot have a default value if we don't have a "defaults" method
            return None
    
    @staticmethod
    def make(name: str,
             validator: ValidatorBase = PassAllValidator(),
             type: ScalarConfigTypeRequirements = None) -> 'ScalarEntry':
        """Create a simple scalar entry

        No type conversion, meaning that the type is used as-is from the config IO layer. However, one or more excepted types 
        may still be specified to indicate that the config file value should have that type. If any type is specified,
        it is checked during conversion. Otherwise, any type is allowed. Type-checking is done before any validators
        are applied. Valid "type" parameters include a single required type, a list of required types, or a custom type checking
        function. It is recommended to use the methods provided by "RequireConfigType", as these cover all supported config types.
        If you manually specify a type that isn't supported as a config object, without whitelisting it in "TypeConfig", type
        checking will always fail.

        Args:
            name (str): key of the value within its composite parent
            validator (ValidatorBase): optional validator
        """
        return ScalarEntry(
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
              validate_when: ValidatorPhase = ValidatorPhase.BeforeConversion,) -> 'ScalarEntry':
        """Create a typed scalar entry

        Create a scalar value that is type-casted to the type specified in "cast_to". The "type" parameter may be used 
        to specify one or more optional required config types that are checked before any validators. The remaining parameters
        are the same as with the untyped scalar, with and added a validation phase parameter that indicates when validation
        should be performed (i.e. before or after type checking). The casted type is checked again after conversion to
        ensure that the returned type matches what is specified above.
        
        Args:
            name (str): key of the value within its composite parent
            cast_to (ConversionTargetType): value target type
            type (ScalarConfigTypeRequirements): expected config object type, optional
            validator (ValidatorBase): optional validator
            validate_when (ValidatorPhase): specify if the validation should happen before or after conversion
        """
        return ScalarEntry(
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
               converted_type: ScalarConvertedTypeRequirements = None) -> 'ScalarEntry':
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
        return ScalarEntry(
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

class Config:

    @staticmethod
    def _make_config_type_checking_function(expected_types: ScalarConfigTypeRequirements, 
                                            default: ConfigTypeCheckingFunction) -> ConfigTypeCheckingFunction:
        if type(expected_types) is list:
            return RequireConfigType.from_type_list(types=expected_types)
        elif callable(expected_types):
            return expected_types  
        elif expected_types:
            return RequireConfigType.from_type_list(types=[expected_types])
        else:
            return default


    @staticmethod
    def _make_converted_type_checking_function(expected_types: ScalarConvertedTypeRequirements, 
                                               default: ConvertedTypeCheckingFunction) -> ConvertedTypeCheckingFunction:
        if type(expected_types) is list:
            return RequireConvertedType.from_type_list(types=expected_types)
        elif callable(expected_types):
            return expected_types  
        elif expected_types:
            return RequireConvertedType.from_type_list(types=[expected_types])
        else:
            return default

    @classmethod
    def scalar(cls,
               validator: ValidatorBase = PassAllValidator(),
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
            config_type_check=cls._make_config_type_checking_function(expected_types=type, default=RequireConfigType.scalar())
        )

    @classmethod
    def typed_scalar(cls,
                     cast_to: ConversionTargetType, 
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
            config_type_check=cls._make_config_type_checking_function(expected_types=type, default=RequireConfigType.scalar()),
            converted_type_check=RequireConvertedType.from_type_list(types=[cast_to]),
        )
    
    @classmethod
    def custom_scalar(cls,
                      converter: ConverterBase,
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
            config_type_check=cls._make_config_type_checking_function(
                expected_types=type, 
                default=RequireConfigType.scalar(),
            ),
            converted_type_check=cls._make_converted_type_checking_function(
                expected_types=converted_type, 
                default=RequireConvertedType.none(),
            ),
        )
    
    
    @staticmethod
    def typed_composite(entries: List[CompositeEntry],
                        cast_to: ConversionTargetType,
                        requirements: _CompositeRequirements or None = None) -> CompositeConfigValue:
        """Create a typed composite value
        
        During the conversion process, the dictionary created by the entry list will be passed to the type's 
        constructor. In other words, if your target type supports a constructor that takes a dictionary with
        values as specified in the entry list, use this method for ease-of-use.

        Additionally, if your target type defines the static methods "required" and "defaults", these are used
        to define which scalar child-values are required, and what there default values will be if they aren't
        required. If your target class doesn't define those methods, and you can't/don't want to add them, it
        is also possible to specify the lists in a _CompositeRequirements object. If you do not specify any 
        requirements, all entries are assumed to be required

        Args:
            entries (List[CompositeEntry]): list of children for this composite
            cast_to (ConversionTargetType): config entry type, must be constructible from a dictionary
            requirements (_CompositeRequirements): optional requirements object
        """
        
        return CompositeConfigValue(
            expected_children=dict([
                entry.create_value(composite_type=cast_to, requirements=requirements) for entry in entries
            ]),
            converter=TypeCastingConverter(to=cast_to),
            converted_type_check=RequireConvertedType.from_type_list(types=[cast_to]),
        )

    @classmethod
    def composite(cls,
                  entries: List[CompositeEntry],
                  converter: ConverterBase = NoOpConverter(),
                  type: ScalarConvertedTypeRequirements = None,
                  requirements: _CompositeRequirements or None = None) -> CompositeConfigValue:
        """Create a composite with a custom type converter
        
        If your target type does not support a dictionary constructor, or you want to perform some complex
        conversion operation, you need to use this method. You can still specify an output type to retrieve
        required and default values, or as above use a _CompositeRequirements object.

        Args:
            entries (List[CompositeEntry]): list of children for this composite
            converter (ConverterBase): type converter, takes a dictionary as its input
            type (ConversionTargetType): optional target type for required and default values
            requirements (_CompositeRequirements): optional requirements object
        """
        
        return CompositeConfigValue(
            expected_children=dict([
                entry.create_value(composite_type=type, requirements=requirements) for entry in entries
            ]),
            converter=converter,
            converted_type_check=cls._make_converted_type_checking_function(
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
        list, composite, or scalar. If you have requirements on the length of the list, specify
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
    
    @classmethod
    def list(cls,
             elements: ConfigValueBase,
             requirements: ListValidator = ListValidator(),
             converter: ConverterBase = NoOpConverter(),
             type: ScalarConvertedTypeRequirements = None):
        """Create a list entry
        
        Each value in the list has the same definition. The values may be any config value: 
        list, composite, or scalar. If you have requirements on the length of the list, specify
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
            converted_type_check=cls._make_converted_type_checking_function(
                expected_types=type,
                default=RequireConvertedType.none(),
            ),
        )
