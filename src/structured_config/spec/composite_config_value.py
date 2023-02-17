
from spec.config_value_base import ConfigValueBase
from conversion.converter_base import ConverterBase
from structured_config.validation.pass_all_validator import PassAllValidator
from conversion.no_op_converter import NoOpConverter
from typedefs import ConfigObjectType, ConversionTargetType
from spec.invalid_child_type_exception import InvalidChildTypeException
from typing import Dict, Tuple

class CompositeConfigValue(ConfigValueBase):
    """Composite config value class
    
    A composite config value is made up of several children, identified by keys.
    Each child may be another composite value, a scalar value, or a list of values.
    Conversion and validation is applied on a child-value level. An additional 
    conversion operation can be applied to the collection of all children, which is
    a dictionary of keys to converted child types. If no converter is specified, the 
    composite value will simply be that dictionary. A composite value is considered 
    optional if it has no required children.

    Args:
        expected_children (Dict[str, ConfigValueBase]): child key-value definitions
        converter (ConverterBase): optional converter for the entire composite value
    """

    def __init__(self,
                 expected_children: Dict[str, ConfigValueBase],
                 converter: ConverterBase = NoOpConverter()):
        self._children: Dict[str, ConfigValueBase] = expected_children
        self._converter: ConverterBase = converter

    def convert(self, input: ConfigObjectType or None, key: str, parent_key: str) -> ConversionTargetType:

        this_key: str = self.extend_key(aggregate=parent_key, key=key)
        values: Dict[str, ConversionTargetType] = {}

        # check for "None": we can still return a valid object if each of
        # the children entries are optional
        if input == None:
            values = dict(
                [(
                    child_key,
                    self._convert_one(
                        value=child, 
                        input=None, 
                        key=child_key, 
                        parent_key=this_key
                    )) for child_key, child in self._children.items()
                ]
            )

        # the config input must be a dictionary if it isn't "None"
        elif type(input) is not dict:
            raise InvalidChildTypeException(
                child_type=type(input), 
                expected_type=Dict[str, ConfigObjectType],
                child_key=key,
                parent_key=parent_key
            )

        # config input is a non-null dictionary, so we can try and convert it
        else:
            values = dict(
                [(
                    child_key,
                    self._convert_one(
                        value=child, 
                        # instead of passing "None" like we did above, we 
                        # try and retrieve the child object from the input
                        # if that fails, we use "None" as the default to 
                        # trigger the default/requirement check in the child
                        input=input.get(child_key, None), 
                        key=child_key, 
                        parent_key=this_key
                    )) for child_key, child in self._children.items()
                ]
            )

        # finally, we apply the conversion to the value dictionary
        return self._converter(other=values)

    def _convert_one(self, 
                     value: ConfigValueBase, 
                     input: ConfigObjectType or None, 
                     key: str, 
                     parent_key: str) -> Tuple[str, ConversionTargetType]:
        return (key, value.convert(
            input=input,
            key=key,
            parent_key=parent_key
        ))
