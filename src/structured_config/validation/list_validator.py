
from typedefs import ConversionTargetType
from validation.validation_exception import ValidationException
from typing import List

class ListValidator:
    """List count and element validator
    
    If you need restrictions on your list values, you can use the ListValidator
    to specify min, max, or strict count restrictions. min or max counts may also be exclusive
    (i.e. len > min or len < max instead of >= and <=). If you need more complex validation
    checks, you can define a subclass of ListValidator and implement "validate" to perform
    any check you require.

    Args:
        min_count (int or None): list min count, optional
        max_count (int or None): list max count, optional
        min_exclusive (bool): should min be exclusive, defaults to False
        max_exclusive (bool): should max be exclusive, defaults to False
        strict_count (int or None): exact required list count, optional
    """

    def __init__(self, 
                 min_count: int or None = None,
                 min_exclusive: bool = False,
                 max_count: int or None = None,
                 max_exclusive: bool = False,
                 strict_count: int or None = None):
        self._min: int or None = min_count
        self._min_exclusive: bool = min_exclusive
        self._max: int or None = max_count
        self._max_exclusive: bool = max_exclusive
        self._strict: int or None = strict_count

    def __call__(self, values: List[ConversionTargetType]) -> List[ConversionTargetType]:
        if not self.validate(values=values):
            raise ValidationException(value=values, reason="List failed to validate with the following data: "
                                      f"{'{'}length={len(values)}, min={self._min}, max={self._max}, strict={self._strict}, "
                                      f"min_exclusive={self._min_exclusive}, max_exclusive={self._max_exclusive}{']'}")
        else:
            return values
        
    def _validate_list(self, values: List[ConversionTargetType]) -> bool:
        return self._limits(values=values) and self.validate(values=values)

    def _limits(self, values: List[ConversionTargetType]) -> bool:
        # check strict count
        if self._strict != None:
            return len(values) == self._strict
        
        within_limits = True
        if self._min != None:
            within_limits = within_limits and (\
                (self._min_exclusive and len(values) > self._min) or \
                (not self._min_exclusive and len(values >= self._min)))
            
        if self._max != None:
            within_limits = within_limits and (\
                (self._max_exclusive and len(values) < self._max) or \
                (not self._max_exclusive and len(values <= self._max)))
            
        return within_limits

    def validate(self, values: List[ConversionTargetType]) -> bool:
        """Custom list validation function, override in subclasses
        
        If you need more complex list validation, derive a subclass from ListValidator
        and implement "validate".
        """
        return True
