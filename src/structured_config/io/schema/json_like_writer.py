
from structured_config.io.schema.indented_schema_writer import IndentedSchemaWriter, IndentationConfig
from structured_config.io.schema.schema_writer_base import ObjectDefinition, ListDefinition, ValueDefinition
from structured_config.spec.config_value_base import ConfigValueBase

from typing import List

class JsonLikeWriter(IndentedSchemaWriter):

    def __init__(self, indentation: IndentationConfig = IndentationConfig()):
        super().__init__(indentation=indentation)

    def construct_next(self, next_indentation: IndentationConfig) -> 'IndentedSchemaWriter':
        return JsonLikeWriter(indentation=next_indentation)

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
            f"{self.indent(offset=1)}\"{key}\": {child.define(self.next())}"
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