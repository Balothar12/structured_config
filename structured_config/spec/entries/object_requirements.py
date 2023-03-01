
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Type, get_type_hints

from structured_config.base.typedefs import ConversionTargetType


@dataclass
class ObjectRequirements:
    required_list: List[str]
    defaults_dict: Dict[str, ConversionTargetType or None]

    def __post_init__(self):
        self.required: Callable[[], List[str]] = self._get_required
        self.defaults: Callable[[], Dict[str, ConversionTargetType]] = self._get_defaults

    def _get_required(self) -> List[str]:
        return self.required_list
    def _get_defaults(self) -> Dict[str, ConversionTargetType or None]:
        return self.defaults_dict
    

class MakeRequirements:
    
    @staticmethod
    def required(required: List[str]):
        return ObjectRequirements(required_list=required, defaults_dict={})
    
    @staticmethod
    def optional(defaults: Dict[str, ConversionTargetType or None]):
        return ObjectRequirements(required_list=[], defaults_dict=defaults)
    
    @staticmethod
    def mixed(required: List[str], defaults: Dict[str, ConversionTargetType or None]):
        return ObjectRequirements(required_list=required, defaults_dict=defaults)

class ExtractRequirements:

    def __init__(self, name: str):
        self._name = name

    def _get_required_method(self, 
                             object_type: ConversionTargetType or None, 
                             requirements: ObjectRequirements or None) -> Any:
        return self._get_method_with_fallback(main=object_type, 
                                              fallback=requirements, 
                                              method="required",
                                              expected_return_type=list)
    
    def _get_defaults_method(self, 
                             object_type: ConversionTargetType or None, 
                             requirements: ObjectRequirements or None) -> Any:
        return self._get_method_with_fallback(main=object_type, 
                                              fallback=requirements, 
                                              method="defaults",
                                              expected_return_type=dict)
    
    def _get_method_with_fallback(self, 
                                  main: Any, 
                                  fallback: Any,
                                  method: str,
                                  expected_return_type: Type) -> Any:
        """Try to get the specified method with the specified return type

        Try the main object first, then try the fallback object. If neither has a matching attribute, 
        return "None", otherwise return the callable attribute.
        """
        method_attr: Any = None
        if main != None:
            attr = getattr(main, method, None)
            if attr != None and callable(attr) and get_type_hints(attr)["return"].__origin__ is expected_return_type:
                method_attr = attr
        if method_attr == None and fallback != None:
            attr = getattr(fallback, method, None)
            if attr != None and callable(attr) and get_type_hints(attr)["return"].__origin__ is expected_return_type:
                method_attr = attr
        return method_attr
    
    def find_required(self, 
                       object_type: ConversionTargetType or None, 
                       requirements: ObjectRequirements or None) -> bool:
        # get the "required" method
        required_method = self._get_required_method(object_type=object_type, requirements=requirements)
        # verify the method
        if callable(required_method) and get_type_hints(required_method)["return"].__origin__ is list:
            # get the default value
            return self._name in required_method()
        else:
            # values are required by default, because the assumption is that if a class
            # doesn't define the "required" method, it won't define the "defaults" method
            # either
            return True

    def find_default(self, 
                       object_type: ConversionTargetType or None, 
                       requirements: ObjectRequirements or None) -> ConversionTargetType:
        # get the "defaults" method
        defaults_method = self._get_defaults_method(object_type=object_type, requirements=requirements)
        # verify the method
        if callable(defaults_method) and get_type_hints(defaults_method)["return"].__origin__ is dict:
            # get the default value
            return defaults_method().get(self._name, None)
        else:
            # we cannot have a default value if we don't have a "defaults" method
            return None