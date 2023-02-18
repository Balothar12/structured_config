
from structured_config.typedefs import ConfigObjectType

class CaseTranslatorBase:

    def translate_keys(self, input: ConfigObjectType) -> ConfigObjectType:
        if type(input) is list:
            return [self.translate_keys(input=element) for element in input]
        elif type(input) is dict:
            return {self.translate(key=key): self.translate_keys(input=value) for key, value in input.items()}
        else:
            return input

    def translate(self, key: str) -> str:
        raise NotImplementedError()