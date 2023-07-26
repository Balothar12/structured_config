
from dataclasses import dataclass
from typing import List, Dict
from structured_config.io.overrides.invalid_override_type_exception import InvalidOverrideTypeException
from structured_config.io.overrides.invalid_override_specification_exception import InvalidOverrideSpecificationException
from structured_config.base.typedefs import ConfigObjectType
import re

@dataclass
class OverrideKeyPart:
    part: str
    array: bool

    @staticmethod
    def from_str_part(str_part: str) -> 'OverrideKeyPart':
        index_pattern: str = r"\[(-1|([0-9])+)\]"
        if str_part == "+":
            return OverrideKeyPart(part="array.add", array=True)
        elif re.search(pattern=index_pattern, string=str_part):
            return OverrideKeyPart(
                part=f"array.set:{re.search(pattern=index_pattern, string=str_part)[1]}",
                array=True,
            )
        else:
            return OverrideKeyPart(part=str_part, array=False)
        
    def __str__(self) -> str:
        return self.part
    
@dataclass
class Override:
    """Config value override
    
    A config value override contains a key referring to a specific config entry, and a corresponding config 
    value (must be str, int, float, or bool). The key is a "."-separated path into the configuration 
    structure. For dictionaries, path elements are simply the keys. For lists, there are two directives: ADD 
    a new element, or SET data on an existing element.

    The ADD directive is invoked by using a "+" on the path-level of the list element:

        config: 
            {
                "addresses": [
                    {
                        "street": "Musterstr"
                    }
                ]
            }

        override key for adding an address and setting the street name:
            "addresses.+.street"

    This will add a new element at the end of the list and set the street name to be the specified value.

    The GET directive is invoked by using "[<index>]" as the path element, where "<index>" is the index of
    the addressed list element:

        config:
            {
                "addresses": [
                    {
                        "street": "Musterstr"
                    },
                    {
                        "street": "Nichtmusterstr"
                    }
                ]
            }

        override key for changing the street name in the second list element:
            "addresses.[1].street"

    This will modify the addressed element if it exists. Otherwise, an exception will be raised.

    When specifying multiple overrides where some SET directive depend on previous ADD directives, 
    the order of application is relevant. This is why the "Mapper" class sorts all overrides before 
    applying them to ensure that all ADD directives are run before the SET directives.  
    """

    key: str
    value: str or int or float or bool

    def __post_init__(self):
        # force type check of "value": we need this to be a scalar type that could be the output
        # of a config file reader, in order to keep consistency with that the converters may expect
        if type(self.value) is not str and type(self.value) is not int and type(self.value) is not float and type(self.value) is not bool:
            raise InvalidOverrideTypeException(location=self.key, type=type(self.value))

    def split_key(self) -> List[OverrideKeyPart]:
        parts: List[str] = self.key.split(".")
        return [OverrideKeyPart.from_str_part(str_part=part) for part in parts]

class Assignment:

    def __init__(self, overrides: List[Override], data: ConfigObjectType):
        self._overrides = overrides
        self._data = data

    def apply(self) -> ConfigObjectType:
        for override in self._overrides:
            self._process_one_override(override=override)
        return self._data

    def _process_one_override(self, override: Override):
        # split key into parts
        key: List[OverrideKeyPart] = override.split_key()

        # start with the data as the current object
        current: ConfigObjectType = self._data

        # go through each part
        for index in range(len(key)):
            
            # check position in key chain
            if index >= len(key) - 1:
                # last key in the chain, we need to assign the value here
                self._assign_value(
                    current_part=key[index], 
                    current_object=current, 
                    value=override.value, 
                    parent_key=".".join([str(k) for k in key[:index]]),
                )
            else:
                # not at the end of the chain yet, we need to keep going
                current = self._advance(
                    current_part=key[index],
                    next_part=key[index + 1],
                    current_object=current,
                    parent_key=".".join([str(k) for k in key[:index]]),
                )

    def _advance(self,
                 current_part: OverrideKeyPart,
                 next_part: OverrideKeyPart,
                 current_object: ConfigObjectType,
                 parent_key: str) -> ConfigObjectType:
        # check part type
        if current_part.array:
            # current stage should be a list
            if type(current_object) is list:
                # current type is correct
                return self._advance_list(
                    current_part=current_part,
                    next_part=next_part,
                    current_object=current_object,
                    parent_key=parent_key
                )
            else:
                # current object is not a list
                raise InvalidOverrideSpecificationException(reason=f"Cannot modify list: element {parent_key} is a "
                                                                   f"{type(current_object).__name__}")
        else:
            # current stage should be a dictionary
            if type(current_object) is dict:
                # current type is correct, we need to access the specified key
                if current_part.part not in current_object:
                    # key not found, check the next key part to find out what kind of value we need to add
                    if next_part.array:
                        current_object[current_part.part] = []
                    else:
                        current_object[current_part.part] = {}
                    # the key exists here either way, so return that value
                return current_object[current_part.part]

            else:
                # current object is not a dictionary
                raise InvalidOverrideSpecificationException(reason=f"Cannot modify key {current_part.part} below "
                                                                   f"{parent_key}: {current_part.part} is type "
                                                                   f"'{type(current_object).__name__}', but should be 'dict'")

    def _advance_list(self,
                      current_part: OverrideKeyPart,
                      next_part: OverrideKeyPart,
                      current_object: List[ConfigObjectType],
                      parent_key: str):
        
        # because we have a list, and want to access either an object or a list
        # next, we need to make sure that the list is either empty, or that all
        # elements are either objects or lists
        if len(current_object) > 0 and (not all([type(e) is list for e in current_object]) and not all([type(e) is dict for e in current_object])):
            raise InvalidOverrideSpecificationException(reason=f"List '{parent_key}' contains mismatched element types, all elements "
                                                               f"must be either objects or lists")

        # get the (empty) object we may need to add to the list
        new: ConfigObjectType = {}
        if next_part.array:
            new = []

        # now check the key operation
        op: str = current_part.part.split(".")[1]
        if op == "add":
            # here we need to check the other types, if the list has any
            if len(current_object) > 0 and type(current_object[0]) is not type(new):
                raise InvalidOverrideSpecificationException(reason=f"List {parent_key} has '{type(current_object[0])}' elements, "
                                                                   f"but a new '{type(new)}' element was requested")

            # now that we know the type matches what's potentially already in the list, 
            # we can add a list entry with the next object
            current_object.append(new)
            return current_object[-1]
        elif op.startswith("set:"):
            # set a specific index
            try:
                # try to get the index and set the value
                index = int(op.split(":")[1])
                return current_object[index]
            except:
                # raise an error if that fails
                raise InvalidOverrideSpecificationException(reason=f"Cannot modify list element with set-operation "
                                                                    f"{op} below parent {parent_key} on a list with "
                                                                    f"{len(current_object)} elements")
        else:
            # invalid key part
            raise InvalidOverrideSpecificationException(reason=f"Key part {current_part.part} is invalid for modifying " 
                                                                       f"list element {parent_key}")

        


    def _assign_value(self, 
                      current_part: OverrideKeyPart, 
                      current_object: ConfigObjectType,
                      value: str or int or float or bool,
                      parent_key: str):
        if current_part.array:
            # current key part is assigning referring to an array entry,
            # so we need to check if the current object is a list
            if type(current_object) is list:
                self._assign_value_to_list(
                    current_part=current_part,
                    current_object=current_object,
                    value=value,
                    parent_key=parent_key,
                )
            else:
                # current object is not a list
                raise InvalidOverrideSpecificationException(reason=f"Cannot modify list: element {parent_key} is a "
                                                                   f"{type(current_object).__name__}")
            
        else:

            # current key part is not an array part, so we need to assign a value to a dictionary
            if type(current_object) is dict:
                # this is very easy: just assign the value to the key
                current_object[current_part.part] = value
            else:
                # current object is not a dictionary
                raise InvalidOverrideSpecificationException(reason=f"Cannot add value {value} with key {current_part.part} below "
                                                                   f"{parent_key}: {current_part.part} is type "
                                                                   f"'{type(current_object).__name__}', but should be 'dict'")
            
        
    def _assign_value_to_list(self, 
                              current_part: OverrideKeyPart, 
                              current_object: List[ConfigObjectType],
                              value: str or int or float or bool,
                              parent_key: str):
        # we have a list, and want to assign this value to that list
        # to ensure that we don't mix scalars with objects in lists (this is
        # not supported by the later specification framework), we check that 
        # the list is either empty, or every element in the list is not another 
        # list, dict, or object
        if len(current_object) > 0 and any([type(e) is list or type(e) is dict or type(e) is object for e in current_object]):
            raise InvalidOverrideSpecificationException(reason=f"List {parent_key} contains objects, but must contain only scalars "
                                                               f"for a scalar override value to be valid")        

        # now check the key operation
        op: str = current_part.part.split(".")[1]
        if op == "add":
            # add a list entry with the specified value
            current_object.append(value) 
        elif op.startswith("set:"):
            # set a specific index
            try:
                # try to get the index and set the value
                index = int(op.split(":")[1])
                current_object[index] = value
            except:
                # raise an error if that fails
                raise InvalidOverrideSpecificationException(reason=f"Cannot set list element value {value} with set-operation "
                                                                    f"{op} below parent {parent_key} on a list with "
                                                                    f"{len(current_object)} elements")
        else:
            # invalid key part
            raise InvalidOverrideSpecificationException(reason=f"Key part {current_part.part} is invalid for modifying " 
                                                                       f"list element {parent_key}")

    