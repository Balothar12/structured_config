
from structured_config.spec.config_value_base import ConfigValueBase
from dataclasses import dataclass, field
from typing import Type, Dict, List
from enum import Enum

class SchemaWriterBase:

    def define(self, config: ConfigValueBase) -> str:
        return config.specify().define(self)

    def define_object(self, obj: 'ObjectDefinition') -> str:
        raise NotImplementedError()
    def define_list(self, list: 'ListDefinition') -> str:
        raise NotImplementedError()
    def define_value(self, value: 'ValueDefinition') -> str:
        raise NotImplementedError()
    
class SpecType(Enum):
    Value = 0
    Object = 1
    List = 2

@dataclass
class DefinitionBase:
    spec_type: SpecType = field(default=False, init=False)

    def define(self, schema_writer: 'SchemaWriterBase') -> str:
        if self.spec_type == SpecType.Value:
            return schema_writer.define_value(self)
        elif self.spec_type == SpecType.List:
            return schema_writer.define_list(self)
        elif self.spec_type == SpecType.Object:
            return schema_writer.define_object(self)
        else:
            return '{}'

@dataclass
class ValueDefinition(DefinitionBase):
    type: Type or None
    required: bool
    default: Type or None

    def __post_init__(self):
        self.spec_type = SpecType.Value

@dataclass
class ObjectDefinition(DefinitionBase):
    children: Dict[str, DefinitionBase]

    def __post_init__(self):
        self.spec_type = SpecType.Object

@dataclass
class ListDefinition(DefinitionBase):
    children: DefinitionBase
    min: int or None
    max: int or None
    min_exclusive: bool
    max_exclusive: bool
    strict: int or None
    limits_summary: str

    def __post_init__(self):
        self.spec_type = SpecType.List

    
