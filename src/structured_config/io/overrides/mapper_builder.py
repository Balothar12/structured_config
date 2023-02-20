
import argparse
from typing import TYPE_CHECKING, Any, Dict, List
from structured_config.io.overrides.argparse_extractor import ArgparseOverrideKeyMappingFunction, ArgparseOverrides, DictionaryKeyFilterFunction
from structured_config.io.overrides.assignment import Override

from structured_config.io.overrides.extractor_base import ExtractorBase
if TYPE_CHECKING:
    from structured_config.io.overrides.mapper import Mapper

class MapperExtractorBuilder:
    """Configure one extractor for override mapping"""

    def __init__(self, mapper_builder: 'MapperBuilder', extractor: ExtractorBase):
        self._builder: MapperBuilder = mapper_builder
        self._extractor: ExtractorBase = extractor
        self._overrides: List[Override] = []

    def only_one(self, key: str, alternate_source: Any or None = None) -> 'MapperExtractorBuilder':
        """Add only one override to the mapper, optionally from a non-default source"""

        if alternate_source == None:
            self._overrides.append(self._extractor.get(key=key))
        else:
            self._overrides.append(self._extractor.get_from_source(key=key, source=alternate_source))
            
        return self
            
    def only(self, keys: List[str], alternate_source: Any or None = None) -> 'MapperExtractorBuilder':
        """Add only the specified list of overrides to the mapper, optionally from a non-default source"""

        if alternate_source == None:
            self._overrides.extend([self._extractor.get(key=key) for key in keys])
        else:
            self._overrides.extend([self._extractor.get_from_source(key=key, source=alternate_source) for key in keys])
            
        return self

    def all(self, alternate_source: Any or None = None) -> 'MapperExtractorBuilder':
        """Add all available overrides to the mapper, optionally from a non-default source"""

        if alternate_source == None:
            self._overrides.extend(self._extractor.all_available())
        else:
            self._overrides.extend(self._extractor.all_available_from_source(source=alternate_source))

        return self

    def apply(self) -> 'MapperBuilder':
        """Apply the configuration and return the builder"""

        self._builder.overrides.extend(self._overrides)
        return self._builder


class MapperBuilder:
    """Build an override mapper from extractors"""

    def __init__(self, mapper: 'Mapper'):
        self._mapper: 'Mapper' = mapper
        self.overrides: List[Override] = []

    def extract(self, extractor: ExtractorBase) -> MapperExtractorBuilder:
        """Configure an arbitrary extractor"""
        return MapperExtractorBuilder(mapper_builder=self, extractor=extractor)
    
    def from_argparse_keylist(self, arguments: argparse.Namespace, list_name: str = "config") -> MapperExtractorBuilder:
        """Configure an argparse key-list extractor 
        
        See ArgparseOverrides.from_list for more detailed information about this functionality.
        """
        return self.extract(ArgparseOverrides.from_list(
            list_name=list_name,
            arguments=arguments,
        ))
    
    def from_argparse_direct(self, 
                             arguments: argparse.Namespace) -> MapperExtractorBuilder:
        """Configure an argparse direct extractor
        
        See ArgparseOverrides.direct for more detailed information about this functionality.
        """
        return self.extract(ArgparseOverrides.direct(
            arguments=arguments,
        ))
    
    def from_argparse_fixed_keymap(self, 
                                   map: Dict[str, str], 
                                   arguments: argparse.Namespace) -> MapperExtractorBuilder:
        """Configure an argparse fixed key-map extractor
        
        See ArgparseOverrides.fixed for more detailed information about this functionality.
        """
        return self.extract(ArgparseOverrides.fixed(
            map=map,
            arguments=arguments,
        ))
    
    def from_argparse_custom_keymap(self, 
                                    keymap: ArgparseOverrideKeyMappingFunction, 
                                    arguments: argparse.Namespace,
                                    key_filter: DictionaryKeyFilterFunction or None = None) -> MapperExtractorBuilder:
        """Configure a custom argparse extractor
        
        See ArgparseOverrides.custom for more detailed information about this functionality.
        """
        return self.extract(ArgparseOverrides.custom(
            mapping=keymap,
            arguments=arguments,
            key_filter=key_filter,
        ))
    
    def apply(self) -> 'Mapper':
        """Apply all configured overrides and return to the mapper"""
        for override in self.overrides:
            self._mapper.direct(override.key, override.value)
        return self._mapper
