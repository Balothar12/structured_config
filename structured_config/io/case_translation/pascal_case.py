
from structured_config.io.case_translation.case_translator_base import CaseTranslatorBase, ConfigObjectType

import stringcase

class PascalCase(CaseTranslatorBase):

    def translate(self, key: str) -> str:
        return stringcase.pascalcase(string=key)
        