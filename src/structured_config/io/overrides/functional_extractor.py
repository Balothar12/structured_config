
from typing import Any, Callable, List, Protocol
from structured_config.io.overrides.assignment import Override
from structured_config.io.overrides.invalid_override_key_type_exception import InvalidOverrideKeyTypeException
from structured_config.io.overrides.extractor_base import ExtractorBase

class StringKeyMappingFunction(Protocol):
    
    def __call__(self, str_key: str, any_source: Any, *payload) -> List[Override]: ...

class SourceConverterFunction(Protocol):

    def __call__(self, source: Any) -> Any: ...

class KeyListFunction(Protocol):

    def __call__(self, source: Any or None) -> List[str]: ...

class FunctionalExtractor(ExtractorBase):
    """Simplified extractor base class

    The FunctionalExtractor helps creating custom extractors by allowing users to simple
    specify a mapping function an default source object in its constructor. It also restricts 
    keys to string, which should be sufficient for most cases

    The mapping function takes a string key, a source, an potential additional payload objects
    which may be provided in the constructor. The key-list may be a fixed list of strings which 
    must be valid for all possible sources, or a function that extracts available keys from a 
    specified source.

    The default source must be specified, but it may be None if you don't want to have a default
    source for your extractor. The payload is a list of optional custom data that may be added to
    your mapping function.
    """

    def __init__(self, 
                 keys: List[str] or KeyListFunction, 
                 mapping: StringKeyMappingFunction, default_source: Any, *payload):
        self._mapping = mapping
        self._payload = (default_source, *payload)
        self._keys = keys

    def _check_key_type(self, key: Any):
        # require string keys
        if type(key) is not str:
            raise InvalidOverrideKeyTypeException(key=key, type=type(key), expected=str)

    def get(self, key: Any) -> List[Override]:
        self._check_key_type(key=key)
        return self._mapping(str(key), *self._payload)
    
    def get_from_source(self, key: Any, source: Any) -> List[Override]:
        self._check_key_type(key=key)
        return self._mapping(str(key), source, *self._payload)
    
    def available_keys(self) -> List[Any]:
        if callable(self._keys):
            source: Any or None = None
            if len(self._payload) > 0:
                source = self._payload[0]
            return self._keys(source=source)
        else:
            return self._keys
        
    def available_keys_for_source(self, source: Any) -> List[Any]:
        if callable(self._keys):
            return self._keys(source=source)
        else:
            return self._keys
    
class SourceConvertingFunctionalExtractor(FunctionalExtractor):
    """Functional extractor with source conversion
    
    This extractor works in the same way as the basic functional extractor, but it
    adds the possibility of converting your source objects before trying to access them.
    For example, dictionaries provide very convenient functions to check and access keys.
    However, your sources may be objects that need to be converted to dictionaries first.
    You can do this by specifying the appropriate conversion function here, and then using
    the extractor as if the internal source type matches any object type you throw at it.
    """
    def __init__(self, 
                 keys: List[str] or KeyListFunction, 
                 source_converter: SourceConverterFunction, 
                 mapping: StringKeyMappingFunction, source: Any, *payload):
        self._converter = source_converter
        converted_payload = (source, *payload)
        if len(converted_payload) > 0:
            converted_payload = (self._converter(source=converted_payload[0]), *converted_payload[1:])
        super().__init__(keys, mapping, *converted_payload)

    def get_from_source(self, key: Any, source: Any) -> List[Override]:
        self._check_key_type(key=key)
        return self._mapping(str(key), self._converter(source=source), *self._payload)
    
    def available_keys_for_source(self, source: Any) -> List[Any]:
        if callable(self._keys):
            return self._keys(source=self._converter(source=source))
        else:
            return self._keys
            
