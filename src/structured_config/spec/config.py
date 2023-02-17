
from structured_config.spec.scalar_config_value import ScalarConfigValue
from structured_config.spec.composite_config_value import CompositeConfigValue
from structured_config.spec.list_config_value import ListConfigValue
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.validation.pass_all_validator import PassAllValidator
from structured_config.validation.validator_base import ValidatorBase, ValidatorPhase
from structured_config.validation.list_validator import ListValidator
from structured_config.conversion.no_op_converter import NoOpConverter
from structured_config.conversion.type_casting_converter import TypeCastingConverter
from structured_config.conversion.converter_base import ConverterBase
from structured_config.typedefs import ConversionSourceType, ConversionTargetType, ConfigObjectType
from dataclasses import dataclass
from typing import List, Tuple, Protocol, get_type_hints, Dict, Any, Type, Callable

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
                 type: ConversionTargetType or None,
                 requirements: _CompositeRequirements or None):
        self._name: str = name
        self._entries: List[CompositeEntry] = entries
        self._converter: ConverterBase = converter
        self._type: ConversionTargetType or None = type
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
                )
            )
    
    @staticmethod
    def typed(name: str,
              entries: List[CompositeEntry],
              type: ConversionTargetType,
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
            type=type,
            requirements=requirements,
        )
    
    @staticmethod
    def basic(name: str,
              entries: List[CompositeEntry],
              converter: ConverterBase = NoOpConverter(),
              type: ConversionTargetType or None = None,
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
                 requirements: ListValidator):
        self._name: str = name
        self._elements: ConfigValueBase = elements
        self._converter: ConverterBase = converter
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
        ))

    @staticmethod
    def typed(name: str,
              elements: ConfigValueBase,
              type: ConversionTargetType,
              requirements: ListValidator = ListValidator()) -> 'MakeListEntry':
        """Create a typed list entry for a composite value

        See the documentation of "Config.typed_list()" for details on typed list config entries.
            
        Args
            name (str): key of the list in the composite
            elements (ConfigValueBase): list element definition
            type (ConversionTargetType): list-constructible target type for this config value
            requirements (ListValidator): list requirements
        """
        return MakeListEntry(
            name=name,
            elements=elements,
            converter=TypeCastingConverter(to=type),
            requirements=requirements,
        )
    
    @staticmethod
    def basic(name: str,
              elements: ConfigValueBase,
              requirements: ListValidator = ListValidator(),
              converter: ConverterBase = ConverterBase()) -> 'MakeListEntry':
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
        )
    
class MakeScalarEntry(CompositeEntry):
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
                                              expected_return_type=list)
    
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
    def basic(name: str,
              type: Type or None = None,
              validator: ValidatorBase = PassAllValidator()) -> 'MakeScalarEntry':
        """Create a simple scalar entry

        No type conversion, meaning that the type is used as-is from the config IO layer.

        Args:
            name (str): key of the value within its composite parent
            validator (ValidatorBase): optional validator
        """
        return MakeScalarEntry(
            name=name,
            create_config_value=lambda required, default: Config.value(
                validator=validator, 
                required=required, 
                default=default,
                type=type
            )
        )

    @staticmethod
    def typed(name: str,
              type: ConversionTargetType,
              validator: ValidatorBase = PassAllValidator(),
              validate_when: ValidatorPhase = ValidatorPhase.BeforeConversion) -> 'MakeScalarEntry':
        """Create a typed scalar entry

        Type from IO layer is passed directly to the constructor of the specified target type
        
        Args:
            name (str): key of the value within its composite parent
            type (ConversionTargetType): value target type
            validator (ValidatorBase): optional validator
            validate_when (ValidatorPhase): specify if the validation should happen before or after conversion
        """
        return MakeScalarEntry(
            name=name,
            create_config_value=lambda required, default: Config.typed_value(
                type=type,
                validator=validator, 
                validate_when=validate_when, 
                required=required, 
                default=default
            )
        )
    
    @staticmethod
    def complex(name: str,
                converter: ConverterBase,
                validator: ValidatorBase = PassAllValidator(),
                validate_when: ValidatorPhase = ValidatorPhase.BeforeConversion) -> 'MakeScalarEntry':
        """Create a complex typed scalar entry

        Here a custom conversion operator may be specified. This converter will be called with the IO-layer value.
        
        Args:
            name (str): key of the value within its composite parent
            converter (ConverterBase): value converter
            validator (ValidatorBase): optional validator
            validate_when (ValidatorPhase): specify if the validation should happen before or after conversion
        """
        return MakeScalarEntry(
            name=name,
            create_config_value=lambda required, default: Config.complex_value(
                converter=converter,
                validator=validator, 
                validate_when=validate_when, 
                required=required, 
                default=default
            )
        )

class Config:

    @staticmethod
    def value(validator: ValidatorBase = PassAllValidator(),
              type: Type or None = None,
              required: bool = True,
              default: ConfigObjectType or None = None) -> ScalarConfigValue:
        """Create a simple scalar value

        No type conversion, meaning that the type is used as-is from the config IO layer. However, an excepted type 
        may still be specified to indicate that the config file value should have that type. If a type is specified,
        it is checked during conversion. Otherwise, any type is allowed.

        Args:
            name (str): key of the value within its composite parent
            validator (ValidatorBase): optional validator
        """
        return ScalarConfigValue(
            validator=validator,
            validator_phase=ValidatorPhase.BeforeConversion,
            converter=NoOpConverter(expected_type=type),
            required=required,
            default=default
        )

    @staticmethod
    def typed_value(type: ConversionTargetType, 
                    validator: ValidatorBase = PassAllValidator(),
                    validate_when: ValidatorPhase = ValidatorPhase.BeforeConversion,
                    required: bool = True,
                    default: ConversionTargetType or None = None) -> ScalarConfigValue:
        """Create a typed scalar value

        Type from IO layer is passed directly to the constructor of the specified target type
        
        Args:
            name (str): key of the value within its composite parent
            type (ConversionTargetType): value target type
            validator (ValidatorBase): optional validator
            validate_when (ValidatorPhase): specify if the validation should happen before or after conversion
        """
        return ScalarConfigValue(
            validator=validator,
            validator_phase=validate_when,
            converter=TypeCastingConverter(to=type),
            required=required,
            default=default
        )
    
    @staticmethod
    def complex_value(converter: ConverterBase,
                      validator: ValidatorBase = PassAllValidator(),
                      validate_when: ValidatorPhase = ValidatorPhase.BeforeConversion,
                      required: bool = True,
                      default: ConversionTargetType or None = None) -> ScalarConfigValue:
        """Create a complex typed scalar value

        Here a custom conversion operator may be specified. This converter will be called with the IO-layer value.
        
        Args:
            name (str): key of the value within its composite parent
            converter (ConverterBase): value converter
            validator (ValidatorBase): optional validator
            validate_when (ValidatorPhase): specify if the validation should happen before or after conversion
        """
        return ScalarConfigValue(
            validator=validator,
            validator_phase=validate_when,
            converter=converter,
            required=required,
            default=default
        )
    
    
    @staticmethod
    def typed_composite(entries: List[CompositeEntry],
                        type: ConversionTargetType,
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
            type (ConversionTargetType): config entry type, must be constructible from a dictionary
            requirements (_CompositeRequirements): optional requirements object
        """
        
        return CompositeConfigValue(
            expected_children=dict([
                entry.create_value(composite_type=type, requirements=requirements) for entry in entries
            ]),
            converter=TypeCastingConverter(to=type),
        )

    @staticmethod
    def composite(entries: List[CompositeEntry],
                  converter: ConverterBase = NoOpConverter(),
                  type: ConversionTargetType or None = None,
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
        )
    
    @staticmethod
    def typed_list(elements: ConfigValueBase,
                   type: ConversionTargetType,
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
            type (ConversionTargetType): list-constructible target type for this config value
            requirements (ListValidator): list requirements

        """
        
        return ListConfigValue(
            child_definition=elements,
            list_requirements=requirements,
            converter=TypeCastingConverter(to=type),
        )
    
    @staticmethod
    def list(elements: ConfigValueBase,
             requirements: ListValidator = ListValidator(),
             converter: ConverterBase = NoOpConverter()):
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
            converter=converter
        )