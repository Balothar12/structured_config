
from structured_config.io.case_translation.case_translator_base import CaseTranslatorBase
from structured_config.io.case_translation.snake_case import SnakeCase
from structured_config.io.schema.indented_schema_writer import IndentedSchemaWriter, IndentationConfig
from structured_config.io.schema.schema_writer_base import ObjectDefinition, ListDefinition, ValueDefinition
from structured_config.spec.config_value_base import ConfigValueBase

from typing import List

class JsonLikeWriter(IndentedSchemaWriter):

    def __init__(self, indentation: IndentationConfig = IndentationConfig(), 
                 with_schema_case: bool = False, 
                 schema_case: CaseTranslatorBase = SnakeCase()):
        super().__init__(indentation=indentation)
        self._schema_case = schema_case
        self._with_schema_case = with_schema_case

    def define(self, config: ConfigValueBase) -> str:
        if self._with_schema_case:
            current_case = config.get_source_case()
            result: str = super().define(config.expect_source_case(source=self._schema_case))
            config.expect_source_case(source=current_case)
            return result
        else:
            return super().define(config)

    def construct_next(self, next_indentation: IndentationConfig) -> 'IndentedSchemaWriter':
        return JsonLikeWriter(indentation=next_indentation, 
                              with_schema_case=self._with_schema_case,
                              schema_case=self._schema_case)

    def define_list(self, list: ListDefinition) -> str:

        # start specification string construction 
        specification: str = f"[{list.limits_summary}\n{self.indent(offset=1)}"
        
        # add child specification
        specification = (f"{specification}{list.children.define(self.next())}")

        # finish list specification
        return f"{specification}\n{self.indent()}]"
    
    def define_object(self, obj: ObjectDefinition) -> str:        
        # start specification string construction 
        specification: str = f"{{\n"

        # get the specification from each child
        speclist: List[str] = [
            f"{self.indent(offset=1)}\"{obj.key_case.translate(key=key)}\": {child.define(self.next())}"
            for key, child in obj.children.items()
        ]
        specification += ',\n'.join(speclist) + "\n"
            
        # close the composite specification
        return f"{specification}{self.indent()}}}"

    
    def define_value(self, value: ValueDefinition) -> str:

        # get requirement string
        requirement: str = "required"
        if not value.required:
            requirement = f"optional, defaults to '{value.default}'"

        # get type string
        type: str = "any-type"
        if value.type != None:
            type = value.type.__name__

        # construct specification
        return f"'{type}' value, {requirement}"