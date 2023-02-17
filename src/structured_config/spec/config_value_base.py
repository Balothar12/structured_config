

from structured_config.typedefs import ConfigObjectType, ConversionTargetType

class ConfigValueBase:

    def __init__(self):
        pass

    def __call__(self, input: ConfigObjectType) -> ConversionTargetType:
        return self.convert(input)

    def convert(self, input: ConfigObjectType or None, key: str, parent_key: str) -> ConversionTargetType:
        """Convert a config object to a converted application object"""
        raise NotImplementedError()
    
    def specify(self, indentation_level: int = 0, indentation_token: str = "  ") -> str:
        """Build a string containing a readable specification of this config value"""
        raise NotImplementedError()
    
    def indent(self, level: int, token: str):
        return token * level

    def extend_key(self, aggregate: str, key: str) -> str:
        if len(aggregate) == 0:
            return key
        else:
            return f"{aggregate}.{key}"
