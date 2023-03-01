
from typing import List
from structured_config.io.case_translation.case_translator_base import CaseTranslatorBase
from structured_config.io.case_translation.no_translation import NoTranslation
from structured_config.io.overrides.assignment import Assignment, Override, OverrideKeyPart
from structured_config.io.overrides.invalid_override_specification_exception import InvalidOverrideSpecificationException
from structured_config.io.overrides.mapper_builder import MapperBuilder
from structured_config.base.typedefs import ConfigObjectType


class Mapper:
    """Map a number of supported key/value pair types to overrides
    
    By default, overrides are case-sensitive, however this can be changed by using a source case
    translator that matches the source case of the targeted specification.
    """

    def __init__(self, source_case: CaseTranslatorBase = NoTranslation()):

        self._overrides: List[Override] = []
        self._source_case = source_case

    def with_source_case(self, source_case: CaseTranslatorBase):
        """Change the source case after construction"""

        # change the source case
        self._source_case = source_case
        # and re-key all overrides
        self._overrides = [
            Override(key=".".join(
                [self._source_case.translate(key=part) for part in override.key.split(".")]
            ), value=override.value) for override in self._overrides
        ]
        return self

    def direct(self, key: str, value: str or int or float or bool) -> 'Mapper':
        """Add a direct key-value override"""
        self._overrides.append(Override(key=".".join(
            [self._source_case.translate(key=part) for part in key.split(".")]
        ), value=value))
        return self

    def apply(self, to: ConfigObjectType) -> ConfigObjectType:
        """Apply all stored overrides"""

        # sort the overrides and apply it to provided data
        self._sort()
        return Assignment(overrides=self._overrides, data=to).apply()
    
    def clear(self) -> 'Mapper':
        """Clear all stored overrides"""
        self.overrides = []
        return self
    
    def build(self) -> MapperBuilder:
        """Start build the mapper
        
        While overrides may be added directly using the "direct()" function, the mapper builder
        allows overrides to be added using extractors, which allows for much more flexible and
        sophisticated config overrides, including integration with argparse. All overrides
        are eventually added to the mapper with "direct()", so case-translation is still applied
        at every step.
        """
        return MapperBuilder(mapper=self)

    def _sort(self):
        self._overrides = sorted(self._overrides, key=self._lex_sort_key)

    def _lex_sort_key(self, override: Override) -> str:
        # We want to sort the overrides lexicographically to ensure consistent
        # application order (since that does make a difference). However, we need 
        # to make sure that any list ADD operations are executed before any list SET
        # operations, to avoid trying to access indices that don't exist yet.
        # To achieve this, we transform the sort key slightly: We replace any "+"
        # "-1", and replace any SET section with the index we try to access.
        parts: List[OverrideKeyPart] = override.split_key()
        full_key: str = ".".join([str(p) for p in parts])
        return ".".join([self._transform_sort_key_part(key=part, full_key=full_key) for part in parts])

    def _transform_sort_key_part(self, key: OverrideKeyPart, full_key: str) -> str:

        if key.array and key.part == "array.add":
            return "0:arrayadd"
        elif key.array and key.part.startswith("array.set:"):
            try:
                return key.part.split(":")[1] + ":arrayset"
            except:
                raise InvalidOverrideSpecificationException(reason=f"Unrecognized array directive '{key.part}' in '{full_key}'")
        else:
            return key.part