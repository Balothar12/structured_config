
from dataclasses import dataclass
from typing import Callable, Dict, List

from structured_config.typedefs import ConversionTargetType


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
