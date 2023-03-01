
from typing import Any, Dict, List, Protocol, Tuple
from structured_config.io.overrides.dictionary_node_classifier import DictionaryNodeClassification, DictionaryNodeClassifier
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
                 data: Dict[str, Any] or List[Any],
                 multidict: bool = False):
        self._node_classifier: DictionaryNodeClassifier = DictionaryNodeClassifier()
        self._multidict: bool = multidict
        super().__init__(lambda source: [k for k in list(source.keys())], self._flatten, mapping, data)

    def _flatten(self, source: Any) -> Any:
        return dict(self._key_value_pairs(current=source, keys=[]))
    
    def _key_value_pairs(self, current: Dict[str, Any] or List[str] or Any, keys: List[str]) -> List[Tuple[str, Any]]:
        pairs: List[Tuple[str, Any]] = []

        # classify the curren node
        combined_key: str = ".".join(keys)
        classification: DictionaryNodeClassification = self._node_classifier.classify(
            value=value, 
            location=combined_key,
            multidict=self._multidict,
        )

        # collect key-value-pairs accordingly
        if classification == DictionaryNodeClassification.Tree:
            for key, value in current.items():
                pairs.extend(self._key_value_pairs(current=value, keys=keys + [key]))
        elif classification == DictionaryNodeClassification.List:
            for i, value in enumerate(current):
                pairs.extend(self._key_value_pairs(current=value, keys=keys + [f"[{i}]"]))
        else:
            pairs.extend([(".".join(keys), current)])
        
        # return all pairs wwith valid keys
        return list(filter(lambda p: len(p[0]) > 1, pairs))
    
    @staticmethod
    def direct(data: Dict[str, Any] or List[Any]):
        return DictionarySourceExtractor(
            mapping=lambda k, s: [s[k]], 
            data=data, 
            multidict=False,
        )
    
    @staticmethod
    def direct_multi(data: Dict[str, Any] or List[Any]):
        return DictionarySourceExtractor(
            mapping=lambda k, s: s[k] if type(s[k]) is list else [s[k]],
            data=data,
            multidict=True,
        )
    