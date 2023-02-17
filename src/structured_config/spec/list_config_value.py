from spec.config_value_base import ConfigValueBase
from conversion.converter_base import ConverterBase
from conversion.no_op_converter import NoOpConverter
from typedefs import ConfigObjectType, ConversionTargetType
from spec.invalid_child_type_exception import InvalidChildTypeException
from validation.list_validator import ListValidator
from typing import List, Tuple

class ListConfigValue(ConfigValueBase):
    """List config value
    
    A list config value is a list of values that each follow one specific config value definition. This
    definition may be a scalar, a list, or a composite. By default, there are no requirements on list 
    length, and if the list element itself is not defined in the config, an empty list is returned instead.
    This behavior can be changed by specifying a ListValidator as list_requirements. If necessary, the entire list 
    can also be converted to another type using a converter, although this doesn't happen by default.
    """

    def __init__(self,
                 child_definition: ConfigValueBase,
                 list_requirements: ListValidator = ListValidator(),
                 converter: ConverterBase = NoOpConverter()):
        self._child_definition: ConfigValueBase = child_definition
        self._requirements: ListValidator = list_requirements
        self._list_converter: ConverterBase = converter

    def convert(self, input: ConfigObjectType or None, key: str, parent_key: str) -> ConversionTargetType:

        this_key: str = self.extend_key(aggregate=parent_key, key=key)
        values: List[ConversionTargetType] = {}

        # check for "None": we return an empty list if the list element itself does not exist
        if input == None:
            values = []

            
        # the config input must be a list if it isn't "None"
        elif type(input) is not list:
            raise InvalidChildTypeException(
                child_type=type(input), 
                expected_type=List[ConfigObjectType],
                child_key=key,
                parent_key=parent_key
            )
        
        # config input is a non-null list, so we can try and convert it
        else:
            values = dict(
                [
                    self._convert_one(
                        value=self._child_definition, 
                        input=data, 
                        key=f"[{i}]", 
                        parent_key=this_key
                    ) for i, data in enumerate(input)
                ]
            )

        # validate the list
        values = self._requirements(values=values)

        # convert the list
        return self._list_converter(other=values)

    def _convert_one(self, 
                     value: ConfigValueBase, 
                     input: ConfigObjectType,
                     key: str, 
                     parent_key: str) -> Tuple[str, ConversionTargetType]:
        return value.convert(
            input=input,
            key=key,
            parent_key=parent_key
        )
