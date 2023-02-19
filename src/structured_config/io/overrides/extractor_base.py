
from typing import Any, List

from structured_config.io.overrides.assignment import Override

class ExtractorBase:
    """Override extractor base class
    
    Override extractors may be used to define transformations from arbitrary structured data, together
    with arbitrary keys, to config overrides. The task of an extractor is to extract data from a source
    using a key as a sort of address, and transform the requested key-data pair into an override.

    Every extractor instance has a default data source, which may be empty. The "get()" function should try
    to access the default data source with the specified key. "get_from_source()" may be used to specify an 
    alternate source to get the data from.

    "available_keys() and "available_keys_for_source()" should return all valid keys for the default source,
    or an alternate source, respectively. "all_available()" and "all_available_from_source()" use these 
    lists of valid keys to collect all overrides that either the default source or an alternate source can
    provide to this extractor.
    """

    def available_keys(self) -> List[Any]:
        """Get a list of all available keys for the default source"""
        raise NotImplementedError()
    def available_keys_for_source(self, source: Any) -> List[Any]:
        """Get a list for all available keys from an alternate source
        
        Args:
            source (Any): the alternate source
        """
        raise NotImplementedError()

    def get(self, key: Any) -> Override:
        """Get an override for a specified (available) key from the default source
        
        Args:
            key (Any): the requested key, must be available
        """
        raise NotImplementedError()
    
    def get_from_source(self, key: Any, source: Any) -> Override:
        """Get an override for a specified (available) key from an alternate source
        
        Args:
            key (Any): the requested key, must be available
            source (Any): the alternate source
        """
        raise NotImplementedError()
    
    def all_available(self) -> List[Override]:
        """Get all available overrides for the default source"""
        return [
           self.get(key=key) for key in self.available_keys()
        ]
    
    def all_available_from_source(self, source: Any) -> List[Override]:
        """Get all available overrides for an alternate source
        
        Args:
            source (Any): the alternate source
        """
        return [
            self.get_from_source(key=key, source=source) for key in self.available_keys_for_source(source=None)
        ]