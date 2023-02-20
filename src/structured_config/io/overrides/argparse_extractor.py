
import argparse
from typing import Any, Protocol, Tuple, Dict, List
from structured_config.io.overrides.assignment import Override
from structured_config.io.overrides.dictionary_source_extractor import DictionarySourceExtractor
from structured_config.io.overrides.extractor_base import ExtractorBase
from structured_config.io.overrides.functional_extractor import SourceConverterFunction, SourceConvertingFunctionalExtractor
from structured_config.io.overrides.invalid_override_source_exception import InvalidOverrideSourceException
from structured_config.io.overrides.invalid_override_source_type_exception import InvalidOverrideSourceTypeException

class DictionaryKeyFilterFunction(Protocol):
    def __call__(self, key: str) -> bool: ...

class _NamespaceToDictionary:

    def __init__(self, key_filter: DictionaryKeyFilterFunction or None = None):
        self._key_filter = key_filter

    def __call__(self, arguments: argparse.Namespace or None) -> Dict[str, Any]:
        if arguments == None:
            return {}
        else:
            return {
                key: value for key, value in self._namespace_to_dict(arguments=arguments).items() if self._key_filter == None or self._key_filter(key=key)
            }
        
    def _namespace_to_dict(self, arguments: Any) -> Dict[str, Any] or Any:
        if type(arguments) is argparse.Namespace: 
            return {
                key: self._namespace_to_dict(arguments=value) for key, value in vars(arguments).items()
            }
        else:
            return arguments
        
class ArgparseOverrideKeyMappingFunction(Protocol):

    def __call__(self, key: str) -> str: ...

class _ArgparseExtractor(DictionarySourceExtractor):
    def __init__(self, 
                 arguments: argparse.Namespace or None, 
                 key_mapping: ArgparseOverrideKeyMappingFunction,
                 key_filter: DictionaryKeyFilterFunction or None = None):
        self._map_keys: ArgparseOverrideKeyMappingFunction = key_mapping
        self._namespace_converter: _NamespaceToDictionary = _NamespaceToDictionary(key_filter=key_filter)
        super().__init__(mapping=self._get_override, 
                         data=self._namespace_converter(arguments))

    def _get_override(self, key: str, any_source: Any) -> Override:
        source_key: str = key
        override_key: str = self._map_keys(key=key)
        return Override(
            key=override_key,
            value=any_source[source_key]
        )

class ArgparseOverrides:
    """Factory functions to create argparse-compatible override extractors"""

    @staticmethod
    def direct(arguments: argparse.Namespace or None = None) -> ExtractorBase:
        """Create a 1-to-1 argparse-to-config override extractor
        
        This is the most basic argparse override extractor: It assumes that all objects contained in 
        the namespace are valid overrides, and have keys that can be directly used as override keys.
        This is likely not applicable for more complex configuration setups.

        Args:
            arguments (argparse.Namespace or None): default argparse data source, optional
        """
        return _ArgparseExtractor(arguments=arguments, key_mapping=lambda key: key)
    
    @staticmethod
    def fixed(map: Dict[str, str], arguments: argparse.Namespace or None = None) -> ExtractorBase:
        """Create a fixed key-to-key mapping between argparse entries and overrides
        
        Instead of assuming that every argparse key perfectly matches a valid override key, this factory
        allows users to specify a fixed key mapping. For example, given an argparse namespace attribute
        "person_first_name", the desired override key may be "person.first_name". These mappings may be 
        specified using the "map" argument of this function. Note that for nested namespaces, the namespace
        is flattened and the attribute names are joined with "."s to create the flat keys. List-elements 
        receive keys in the format "[<index>]".
        
        Args:
            map (Dict[str, str]): key map from argparse attribute names (may be nested and concatenated with "."s) to override keys
            arguments (argparse.Namespace or None): default argparse data source, optional
        """
        return _ArgparseExtractor(arguments=arguments, key_mapping=lambda key: map[key], key_filter=lambda key: key in map)
    
    @staticmethod
    def custom(mapping: ArgparseOverrideKeyMappingFunction, 
               arguments: argparse.Namespace or None = None,
               key_filter: DictionaryKeyFilterFunction or None = None) -> ExtractorBase:
        """Create a fully customizable argparse to override mapping
        
        This function gives users full flexibility in how the argparse attributes should be mapped to override keys. 
        Instead of a simple map, a mapping function is now used, which takes an argparse namespace key, and returns an
        override key. Note that for nested namespaces, the namespace is flattened and the attribute names are joined 
        with "."s to create the flat keys. List-elements receive keys in the format "[<index>]". An optional key filter
        may be used to remove any keys from the flattened namespace data source before it is used to retrieve override
        values.

        Args:
            mapping (ArgparseOverrideKeyMappingFunction): key mapping function
            arguments (argparse.Namespace or None): default argparse data source, optional
            key_filter (DictionaryKeyFilterFunction or None): optional key filter function
        
        """
        return _ArgparseExtractor(arguments=arguments, key_mapping=mapping, key_filter=key_filter)
    
    @classmethod
    def from_list(cls,
                  list_name: str = "override",
                  arguments: argparse.Namespace or None = None) -> ExtractorBase:
        """Create a list-based argparse override extractor
        
        The from_list factory function create an extractor that expects a very specific data structure to be present
        in the namespace: A list containing lists of exactly two elements, where the first element represents the
        override key, and the second element represents the override value. This data structure can be added with
        the following argparse config:

        parser.add_argument("--override", nargs=2, action="append")

        The point of this approach is to allow users full flexibility in overriding any config value they want, while
        also providing full transparency what they are overriding. For example, if a user wants to override 
        person.first_name and person.last_name, they would need to specify the following CLI options:

        python <program>                            \\
            --override person.first_name Max        \\
            --override person.last_name Mustermann

        Because the specified keys are directly passed to the override parser, any supported override syntax may be used:

        python <program>                                                    \\
            --override addresses.+.street   Musterstr                       \\
            --override addresses.[0].number 10a                             \\
            --override addresses.[0].zip    12345                           \\
            --override addresses.[0].city   Berlin                          \\
            --override addresses.[0].occupants.+.first_name     Max         \\
            --override addresses.[0].occupants.[0].last_name    Mustermann

        The "list_name" parameter in the factory function indicates the name of the override list in the argparse namespace
        ("overrides" in this example). The "arguments" parameter is again the default namespace data source.

        Args:
            list_name (str): name of the override list in the argparse namespace
            arguments (argparse.Namespace or None): default data source
        """
        return SourceConvertingFunctionalExtractor(
            lambda source: list(source.keys()),
            cls._arguments_to_override_list_converter(list_name=list_name), 
            lambda str_key, any_source: Override(key=str_key, value=any_source[str_key]),
            arguments,
        )

    @classmethod
    def _arguments_to_override_list_converter(cls, list_name: str) -> SourceConverterFunction:
        def convert(source: Any) -> Any:
            return cls._convert_namespace(source=source, list_name=list_name)
        return convert
    
    @staticmethod
    def _convert_namespace(source: Any, list_name: str):
        if source == None:
            return {}
        elif type(source) is not argparse.Namespace:
            raise InvalidOverrideSourceTypeException(source_type=type(source), expected_type=argparse.Namespace)
        else:
            list: List[List[str]] = getattr(source, list_name, [])
            if list == None:
                list = []
            # we need to make sure each list element is a list with two elements
            if not all([len(l) == 2 for l in list]):
                raise InvalidOverrideSourceException(reason=f"Argparse list override must be a list with two-element list, each "
                                                            f"containing the override key and value")
            return {l[0]: l[1] for l in list}

