

from structured_config.base.typedefs import ConfigObjectType, ConversionTargetType
from structured_config.io.case_translation.case_translator_base import CaseTranslatorBase
from structured_config.io.case_translation.no_translation import NoTranslation

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from structured_config.io.schema.schema_writer_base import DefinitionBase

class ConfigValueBase:

    def __init__(self): ...

    def __call__(self, input: ConfigObjectType) -> ConversionTargetType:
        return self.convert(input)
    
    def require_target_case(self, target: CaseTranslatorBase) -> 'ConfigValueBase':
        return self.translate_case(target=target, source=self.get_source_case())
    
    def expect_source_case(self, source: CaseTranslatorBase) -> 'ConfigValueBase':
        return self.translate_case(target=self.get_target_case(), source=source)

    def translate_case(self, target: CaseTranslatorBase, source: CaseTranslatorBase = NoTranslation()) -> 'ConfigValueBase':
        self._target_case: CaseTranslatorBase = target
        self._source_case: CaseTranslatorBase = source
        return self
    
    def translate_to_target(self, key: str) -> str:
        return self.get_target_case().translate(key=key)

    def translate_to_source(self, key: str) -> str:
        return self.get_source_case().translate(key=key)
        
    def get_target_case(self) -> CaseTranslatorBase:
        return getattr(self, "_target_case", NoTranslation())
    def get_source_case(self) -> CaseTranslatorBase:
        return getattr(self, "_source_case", NoTranslation())

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
