
from structured_config.io.case_translation.case_translator_base import CaseTranslatorBase
from structured_config.io.case_translation.pascal_case import PascalCase
from structured_config.io.schema.indented_schema_writer import IndentedSchemaWriter, IndentationConfig
from structured_config.io.schema.schema_writer_base import ObjectDefinition, ListDefinition, ValueDefinition, SpecType
from structured_config.spec.config_value_base import ConfigValueBase

from typing import List


class YamlLikeWriter(IndentedSchemaWriter):

    def __init__(self, 
                 indentation: IndentationConfig = IndentationConfig(), 
                 with_schema_case: bool = False, 
                 schema_case: CaseTranslatorBase = PascalCase()):
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
        return YamlLikeWriter(indentation=next_indentation, 
                              with_schema_case=self._with_schema_case,
                              schema_case=self._schema_case)

    def define_list(self, list: ListDefinition) -> str:
        # first, process the list with reset indentation
        no_indent: YamlLikeWriter = YamlLikeWriter(indentation=IndentationConfig(level=0, token=self.indentation.token))

        # then, split the list by "\n"
        lines: List[str] = list.children.define(no_indent).split("\n")

        # now add "- " to the first entry, and "  " to all others (if there are any others)
        lines[0] = "- " + lines[0]        
        if len(lines) > 1:
            lines[1:] = ["  " + line for line in lines[1:]]

        # finally, add the next indentation to all lines
        lines = [self.indent() + line for line in lines]

        # and join the lines again
        return "\n".join(lines)
    
    def define_object(self, obj: ObjectDefinition) -> str:  

        # get the specification from each child
        speclist: List[str] = []
        for key, child in obj.children.items():
            trailing: str = ""
            if child.spec_type != SpecType.Value:
                trailing = "\n"
            speclist.append(f"{self.indent()}{obj.key_case.translate(key=key)}: {trailing}{child.define(self.next())}")

        # join with newlines
        return "\n".join(speclist)

    
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