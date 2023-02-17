
from structured_config.io.schema.schema_writer_base import SchemaWriterBase
from dataclasses import dataclass

@dataclass
class IndentationConfig:
    level: int = 0
    token: str = "  "

    def next(self) -> 'IndentationConfig':
        return IndentationConfig(
            level=self.level + 1, 
            token=self.token,
        )

class IndentedSchemaWriter(SchemaWriterBase):

    def __init__(self, indentation: IndentationConfig):
        self.indentation = indentation

    def construct_next(self, next_indentation: IndentationConfig) -> 'IndentedSchemaWriter':
        raise NotImplementedError()

    def next(self, next_indentation: IndentationConfig):
        return self.construct_next(next_indentation=next_indentation)
    
    def indent(self, offset: int = 0):
        return self.indentation.token * (self.indentation.level + offset)

    
