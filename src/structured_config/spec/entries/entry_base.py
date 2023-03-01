
from typing import Dict, List, Tuple
from structured_config.spec.config_value_base import ConfigValueBase
from structured_config.spec.entries.object_requirements import ObjectRequirements
from structured_config.typedefs import ConversionTargetType


class EntryBase:
    """Base class for object entries

    Subclasses implement the create_value function, which will return a (name, value) tuple
    with the defined config value. The "object_type" and "requirements" parameters are 
    required only for scalar entries.
    """

    def create_value(self, 
                     object_type: ConversionTargetType or None, 
                     requirements: ObjectRequirements or None) -> Tuple[str, ConfigValueBase]:
        """Create the config value

        This function will be overridden in the base classes. object_type and requirements are
        only relevant for scalar entries. If the object_type defines required() and defaults() 
        static methods, returning a List[str] and Dict[str, Type], respectively, they will be used to
        determine if a key is required, and the default value of that key. If either of these functions 
        are not defined, the requirements object will be used to check any user-defined requirements.
        If that object is not specified, the value is treated as required by default.
        """
        raise NotImplementedError()

    @staticmethod
    def requirements(self, required: List[str], defaults: Dict[str, ConversionTargetType or None]) -> object:
        return ObjectRequirements(required_list=required, defaults_dict=defaults)
