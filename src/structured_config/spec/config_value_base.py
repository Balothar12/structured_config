

from structured_config.typedefs import ConfigObjectType, ConversionTargetType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from structured_config.io.schema.schema_writer_base import DefinitionBase

class ConfigValueBase:

    def __init__(self):
        pass

    def __call__(self, input: ConfigObjectType) -> ConversionTargetType:
        return self.convert(input)

    def convert(self, input: ConfigObjectType or None, key: str = "", parent_key: str = "") -> ConversionTargetType:
        """Convert a config object to a converted application object"""
        raise NotImplementedError()
    
    def specify(self) -> 'DefinitionBase':
        """Get the specification definition object"""
        raise NotImplementedError()
    
    def indent(self, level: int, token: str):
        return token * level

    def extend_key(self, aggregate: str, key: str) -> str:
        if len(aggregate) == 0:
            return key
        else:
            return f"{aggregate}.{key}"
