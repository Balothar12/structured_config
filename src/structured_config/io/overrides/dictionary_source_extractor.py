
from typing import Any, Dict, List, Protocol, Tuple
from structured_config.io.overrides.functional_extractor import SourceConvertingFunctionalExtractor, StringKeyMappingFunction

class DictionaryKeyExtractorFunction(Protocol):
    
    def __call__(self, key: str) -> str: ...

class DictionarySourceExtractor(SourceConvertingFunctionalExtractor):
    """Extractor working on dictionaries
    
    This extractor type functions solely by using dictionaries as both its internal and 
    external source types. Complex dictionaries are automatically flattened by joining keys
    with ".". Any lists in the dictionaries will receive a "[<index>]" key in the flattened
    dictionary. While this matches the override list SET directive, it does not create any
    list entries that may be missing in the config specification: In order words, if you use
    a dictionary source extractor with lists somewhere in the hierarchy, make sure that any 
    list elements addressed in the overrides already exist in the loaded configuration.

    The mapping function fulfils the same task as in the functional extractor: take a key and 
    source, and return the addressed value.

    The data parameter is the default source, and it should be a dictionary or list. This source
    is flattened as described above, which is the internal data source used to actually retrieve
    override values.
    """

    def __init__(self, 
                 mapping: StringKeyMappingFunction, 
                 data: Dict[str, Any] or List[Any]):
        super().__init__(lambda source: [k for k in list(source.keys())], self._flatten, mapping, data)

    def _flatten(self, source: Any) -> Any:
        return dict(self._key_value_pairs(current=source, keys=[]))
    
    def _key_value_pairs(self, current: Dict[str, Any] or List[str], keys: List[str]) -> List[Tuple[str, Any]]:
        pairs: List[Tuple[str, Any]] = []

        if type(current) is dict:
            for key, value in current.items():
                pairs.extend(self._key_value_pairs(current=value, keys=keys + [key]))
        if type(current) is list:
            for i, value in enumerate(current):
                pairs.extend(self._key_value_pairs(current=value, keys=keys + [f"[{i}]"]))
        else:
            pairs.extend([(".".join(keys), current)])
        
        return list(filter(lambda p: len(p[0]) > 1, pairs))
    
    @staticmethod
    def direct(data: Dict[str, Any] or List[Any]):
        return DictionarySourceExtractor(mapping=lambda k, s: s[k], data=data)