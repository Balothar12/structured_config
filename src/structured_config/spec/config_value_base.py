

from typedefs import ConfigObjectType, ConversionTargetType

class ConfigValueBase:

    def __init__(self):
        pass

    def __call__(self, input: ConfigObjectType) -> ConversionTargetType:
        return self.convert(input)

    def convert(self, input: ConfigObjectType or None, key: str, parent_key: str) -> ConversionTargetType:
        raise NotImplementedError()

    def extend_key(self, aggregate: str, key: str) -> str:
        if len(aggregate) == 0:
            return key
        else:
            return f"{aggregate}.{key}"
