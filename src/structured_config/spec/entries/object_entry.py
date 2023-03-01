from typing import List, Tuple
from structured_config.conversion.converter_base import ConverterBase
from structured_config.conversion.no_op_converter import NoOpConverter
from structured_config.conversion.type_casting_converter import TypeCastingConverter
from structured_config.spec.config import Config
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.spec.entries.entry_base import EntryBase
from structured_config.spec.entries.object_requirements import ObjectRequirements
from structured_config.spec.object_config_value import ObjectConfigValue
from structured_config.type_checking.require_types import RequireConvertedType
from structured_config.typedefs import ConversionTargetType, ScalarConvertedTypeRequirements


class _ObjectEntry(EntryBase):
    """Create an object entry for an object config value"""

    def __init__(self,
                 name: str,
                 entries: List[EntryBase],
                 converter: ConverterBase,
                 type: ScalarConvertedTypeRequirements,
                 requirements: ObjectRequirements or None):
        self._name: str = name
        self._entries: List[EntryBase] = entries
        self._converter: ConverterBase = converter
        self._type: ScalarConvertedTypeRequirements = type
        self._requirements: ObjectRequirements or None = requirements
        
        
    def create_value(self, 
                     object_type: ConversionTargetType or None, 
                     requirements: ObjectRequirements or None) -> Tuple[str, ConfigValueBase]:
        """Create a (name, value) tuple for the defined object config value
        """
        return (self._name,
                ObjectConfigValue(
                    expected_children=dict([
                        entry.create_value(object_type=self._type, requirements=self._requirements) for entry in self._entries
                    ]),
                    converter=self._converter,
                    converted_type_check=RequireConvertedType.make_type_checking_function(
                        expected_types=self._type,
                        default=RequireConvertedType.none(),
                    ),
                )
            )
    
class ObjectEntry:

    @staticmethod
    def typed(name: str,
              entries: List[EntryBase],
              cast_to: ConversionTargetType,
              requirements: ObjectRequirements or None = None) -> '_ObjectEntry':
        """Create a typed list entry for an object value

        See the documentation of "Config.typed_object()" for details on typed object config entries.
            
        Args
            name (str): key of the entry in the object
            entries (List[ObjectEntry]): list of children for this object
            type (ConversionTargetType): config entry type, must be constructible from a dictionary
            requirements (ObjectRequirements): optional requirements object
        """
        return _ObjectEntry(
            name=name,
            entries=entries,
            converter=TypeCastingConverter(to=type),
            type=cast_to,
            requirements=requirements,
        )
    
    @staticmethod
    def make(name: str,
             entries: List[EntryBase],
             converter: ConverterBase = NoOpConverter(),
             type: ScalarConvertedTypeRequirements = None,
             requirements: ObjectRequirements or None = None) -> '_ObjectEntry':
        """Create an object entry for an object value

        See the documentation of "Config.object()" for details on object config entries.
        
        Args
            name (str): key of the list in the object
            entries (List[ObjectEntry]): list of children for this object
            converter (ConverterBase): type converter, takes a dictionary as its input
            type (ConversionTargetType): optional target type for required and default values
            requirements (ObjectRequirements): optional requirements object
        """
        return _ObjectEntry(
            name=name,
            entries=entries,
            converter=converter,
            type=type,
            requirements=requirements,
        )
    