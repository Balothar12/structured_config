from structured_config.io.case_translation.case_translator_base import CaseTranslatorBase
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.io.schema.schema_writer_base import ListDefinition
from structured_config.conversion.converter_base import ConverterBase
from structured_config.conversion.no_op_converter import NoOpConverter
from structured_config.type_checking.config_type_checker import ConfigTypeChecker
from structured_config.type_checking.require_types import RequireConfigType
from structured_config.type_checking.type_config import ConfigTypeCheckingFunction, ConvertedTypeCheckingFunction, TypeConfig
from structured_config.typedefs import ConfigObjectType, ConversionTargetType
from structured_config.spec.invalid_child_type_exception import InvalidChildTypeException
from structured_config.validation.list_validator import ListValidator
from structured_config.spec.required_value_not_found_exception import RequiredValueNotFoundException
from typing import List, Tuple, Any

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from structured_config.io.schema.schema_writer_base import DefinitionBase

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
                 config_type_check: ConfigTypeCheckingFunction = RequireConfigType.list(),
                 converted_type_check: ConvertedTypeCheckingFunction = TypeConfig.no_converted_checks(),
                 list_requirements: ListValidator = ListValidator(),
                 converter: ConverterBase = NoOpConverter(),
                 required: bool = True,
                 default: ConversionTargetType or None = None):
        self._config_type_check: ConfigTypeCheckingFunction = config_type_check
        self._converted_type_check: ConvertedTypeCheckingFunction = converted_type_check
        self._child_definition: ConfigValueBase = child_definition
        self._requirements: ListValidator = list_requirements
        self._list_converter: ConverterBase = converter
        self._required = required
        self._default = default

    def specify(self) -> 'DefinitionBase':
        return ListDefinition(
            key_case=self.get_source_case(),
            children=self._child_definition.specify(),
            min=self._requirements.min,
            max=self._requirements.max,
            min_exclusive=self._requirements.min_exclusive,
            max_exclusive=self._requirements.max_exclusive,
            strict=self._requirements.strict,
            limits_summary=self._requirements.specify(),
        )

    def convert(self, input: ConfigObjectType or None, key: str = "", parent_key: str = "") -> ConversionTargetType:

        this_key: str = self.extend_key(aggregate=parent_key, key=key)
        values: List[ConversionTargetType] = {}

        # check for "None"
        if input == None:
            # raise an exception if a required list is not specified at all
            if self._required:
                raise RequiredValueNotFoundException(value_name=f"'{key}' under '{parent_key}'")
            # otherwise we return the default value
            else:
                return self._default

            
        # # validate the config type
        # elif type(input) is not list:
        #     raise InvalidChildTypeException(
        #         child_type=type(input), 
        #         expected_type=List[ConfigObjectType],
        #         child_key=key,
        #         parent_key=parent_key
        #     )
        
        # config input is a non-null list, so we can try and convert it
        else:
            # validate the config type
            self._config_type_check(key=key, parent_key=parent_key, obj=input, scalar=False)

            values = [
                self._convert_one(
                    value=self._child_definition, 
                    input=data, 
                    key=f"[{i}]", 
                    parent_key=this_key
                ) for i, data in enumerate(input)
            ]

        # validate the list
        values = self._requirements(values=values)

        # convert the list
        output = self._list_converter(other=values, parent=parent_key, current=key)

        # check converted list type
        self._converted_type_check(key=key, parent_key=parent_key, obj=output)

        return output

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

    def translate_case(self, target: CaseTranslatorBase, source: CaseTranslatorBase = ...) -> 'ConfigValueBase':
        super().translate_case(target, source)
        self._child_definition.translate_case(target=target, source=source)
        return self