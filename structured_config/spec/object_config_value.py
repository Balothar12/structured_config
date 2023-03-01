
from structured_config.io.case_translation.case_translator_base import CaseTranslatorBase
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.io.schema.schema_writer_base import ObjectDefinition
from structured_config.spec.list_config_value import ListConfigValue
from structured_config.conversion.converter_base import ConverterBase
from structured_config.type_checking.require_types import RequireConfigType
from structured_config.type_checking.type_config import ConfigTypeCheckingFunction, ConvertedTypeCheckingFunction, TypeConfig
from structured_config.validation.pass_all_validator import PassAllValidator
from structured_config.conversion.no_op_converter import NoOpConverter
from structured_config.base.typedefs import ConfigObjectType, ConversionTargetType
from structured_config.spec.invalid_child_type_exception import InvalidChildTypeException
from typing import Dict, Tuple, List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from structured_config.io.schema.schema_writer_base import DefinitionBase

class ObjectConfigValue(ConfigValueBase):
    """Object config value class
    
    An object config value is made up of several children, identified by keys.
    Each child may be another object value, a scalar value, or a list of values.
    Conversion and validation is applied on a child-value level. An additional 
    conversion operation can be applied to the collection of all children, which is
    a dictionary of keys to converted child types. If no converter is specified, the 
    object value will simply be that dictionary. An object value is considered 
    optional if it has no required children.

    Args:
        expected_children (Dict[str, ConfigValueBase]): child key-value definitions
        converter (ConverterBase): optional converter for the entire object value
    """

    def __init__(self,
                 expected_children: Dict[str, ConfigValueBase],
                 config_type_check: ConfigTypeCheckingFunction = RequireConfigType.object(),
                 converted_type_check: ConvertedTypeCheckingFunction = TypeConfig.no_converted_checks(),
                 converter: ConverterBase = NoOpConverter()):
        self._config_type_check: ConfigTypeCheckingFunction = config_type_check
        self._converted_type_check: ConvertedTypeCheckingFunction = converted_type_check
        self._children: Dict[str, ConfigValueBase] = expected_children
        self._converter: ConverterBase = converter

    def specify(self) -> 'DefinitionBase':
        return ObjectDefinition(
            key_case=self.get_source_case(),
            children={key: value.specify() for key, value in self._children.items()},
        )

    def convert(self, input: ConfigObjectType or None, key: str = "", parent_key: str = "") -> ConversionTargetType:

        this_key: str = self.extend_key(aggregate=parent_key, key=key)
        values: Dict[str, ConversionTargetType] = {}

        # check for "None": we can still return a valid object if each of
        # the children entries are optional
        if input == None:
            values = dict(
                [
                    self._convert_one(
                        value=child, 
                        input=None, 
                        key=self.translate_to_source(key=child_key), 
                        parent_key=this_key
                    ) for child_key, child in self._children.items()
                ]
            )

        # # the config input must be a dictionary if it isn't "None"
        # elif type(input) is not dict:
        #     raise InvalidChildTypeException(
        #         child_type=type(input), 
        #         expected_type=Dict[str, ConfigObjectType],
        #         child_key=key,
        #         parent_key=parent_key
        #     )

        # config input is a non-null dictionary, so we can try and convert it
        else:
            # validate config type
            self._config_type_check(key=key, parent_key=parent_key, obj=input, scalar=False)

            values = dict(
                [
                    self._convert_one(
                        value=child, 
                        # instead of passing "None" like we did above, we 
                        # try and retrieve the child object from the input
                        # if that fails, we use "None" as the default to 
                        # trigger the default/requirement check in the child
                        input=input.get(self.translate_to_source(child_key), None), 
                        key=self.translate_to_source(child_key), 
                        parent_key=this_key
                    ) for child_key, child in self._children.items()
                ]
            )

        # finally, we apply the conversion to the value dictionary
        output = self._converter(other=values, parent=parent_key, current=key)

        # check converted type
        self._converted_type_check(key=key, parent_key=parent_key, obj=output)

        return output

    def _convert_one(self, 
                     value: ConfigValueBase, 
                     input: ConfigObjectType or None, 
                     key: str, 
                     parent_key: str) -> Tuple[str, ConversionTargetType]:
        # Apply case translation to the key: this way the original case will be checked
        # as required, but the user-specified conversion routines will receive the key in 
        # the case they expect.
        return (self.translate_to_target(key=key), value.convert(
            input=input,
            key=key,
            parent_key=parent_key
        ))
    
    def translate_case(self, target: CaseTranslatorBase, source: CaseTranslatorBase = ...) -> 'ConfigValueBase':
        super().translate_case(target, source)
        for child in self._children.values():
            child.translate_case(target=target, source=source)
        return self
