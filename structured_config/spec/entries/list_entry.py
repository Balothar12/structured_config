
from typing import Tuple
from structured_config.conversion.converter_base import ConverterBase
from structured_config.conversion.no_op_converter import NoOpConverter
from structured_config.conversion.type_casting_converter import TypeCastingConverter
from structured_config.spec.config import Config
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.spec.entries.entry_base import EntryBase
from structured_config.spec.entries.object_requirements import ExtractRequirements, ObjectRequirements
from structured_config.spec.list_config_value import ListConfigValue
from structured_config.type_checking.require_types import RequireConvertedType
from structured_config.base.typedefs import ConversionTargetType, ScalarConvertedTypeRequirements
from structured_config.validation.list_validator import ListValidator


class _ListEntry(EntryBase):
    """Create a list entry for an object config value"""

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
        self._requirement_extractor: ExtractRequirements = ExtractRequirements(name=self._name)
        
    def create_value(self, 
                     object_type: ConversionTargetType or None, 
                     requirements: ObjectRequirements or None) -> Tuple[str, ConfigValueBase]:
        """Create a (name, value) tuple for the defined list config value
        """
        return (self._name, ListConfigValue(
            child_definition=self._elements,
            list_requirements=self._requirements,
            converter=self._converter,
            converted_type_check=RequireConvertedType.make_type_checking_function(
                expected_types=self._type,
                default=RequireConvertedType.none(),
            ),
            required=self._requirement_extractor.find_required(
                object_type=object_type,
                requirements=requirements,
            ),
            default=self._requirement_extractor.find_default(
                object_type=object_type,
                requirements=requirements,
            ),
        ))

class ListEntry:

    @staticmethod
    def typed(name: str,
              elements: ConfigValueBase,
              cast_to: ConversionTargetType,
              requirements: ListValidator = ListValidator()) -> '_ListEntry':
        """Create a typed list entry for an object value

        See the documentation of "Config.typed_list()" for details on typed list config entries.
            
        Args
            name (str): key of the list in the object
            elements (ConfigValueBase): list element definition
            cast_to (ConversionTargetType): list-constructible target type for this config value
            requirements (ListValidator): list requirements
        """
        return _ListEntry(
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
             type: ScalarConvertedTypeRequirements = None) -> '_ListEntry':
        """Create a list entry for an object value

        See the documentation of "Config.list()" for details on list config entries.
        
        Args
            name (str): key of the list in the object
            elements (ConfigValueBase): list element definition
            requirements (ListValidator): list requirements
            converter (ConverterBase): optional converter to convert the list into another type
        """
        return _ListEntry(
            name=name,
            elements=elements,
            converter=converter,
            requirements=requirements,
            type=type,
        )
    