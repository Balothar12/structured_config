
from enum import Enum
import itertools
from typing import Any, Callable, List, Type

class DictionaryNodeClassification(Enum):
    Leaf = 0b0001
    Tree = 0b0010
    List = 0b0100
    MultiLeaf = 0b1000

class InconsistentDictionaryListNode(Exception):
    def __init__(self, location: str):
        super().__init__(f"List '{location}' in dictionary has inconsistent element classifications: "
                         "All elements must be either list nodes, tree nodes, leaf nodes, or multileaf nodes")

class DictionaryNodeClassifier:

    def __init__(self):

        self._tree_type: Type = dict
        self._list_type: Type = list

    def classify(self, value: Any, location: str, multidict: bool) -> DictionaryNodeClassification:
        if type(value) is self._tree_type:
            return DictionaryNodeClassification.Leaf
        elif type(value) is self._list_type:
            return self._classify_list(list=value, location=location, multidict=multidict)
        else:
            return DictionaryNodeClassification.Leaf

    def _classify_list(self, list: List[Any], location: str, multidict: bool) -> DictionaryNodeClassification:
        # classify all list elements
        classifications: List[DictionaryNodeClassification] = [
            self.classify(
                value=value, 
                location=".".join(
                    location.split(".") + [f"[{index}]"]
                )
            ) for index, value in enumerate(list)
        ]

        # validate the classifications
        self._verify_list_validity(list=classifications, location=location)

        # determine the type
        if all([c == DictionaryNodeClassification.Leaf for c in classifications]):
            return DictionaryNodeClassification.MultiLeaf if multidict else DictionaryNodeClassification.List
        else:
            return DictionaryNodeClassification.List

    def _list_element_types(self, list: List[Any]) -> List[Type]:
        return [type(element) for element in list]
    
    def _list_has_same_elements(self, list: List[Any]) -> bool:
        grouped = itertools.groupby(list)
        return next(grouped, True) and not next(grouped, False)
    
    def _verify_list_validity(self, list: List[DictionaryNodeClassification], location: str):
        if not self._list_has_same_elements(list=list):
            raise InconsistentDictionaryListNode(location=location)