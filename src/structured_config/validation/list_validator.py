
from structured_config.typedefs import ConversionTargetType
from structured_config.validation.validation_exception import ValidationException
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
        self.min: int or None = min_count
        self.min_exclusive: bool = min_exclusive
        self.max: int or None = max_count
        self.max_exclusive: bool = max_exclusive
        self.strict: int or None = strict_count

    def __call__(self, values: List[ConversionTargetType]) -> List[ConversionTargetType]:
        if not self._validate_list(values=values):
            raise ValidationException(value=values, reason="List failed to validate with the following data: "
                                      f"{'{'}length={len(values)}, min={self.min}, max={self.max}, strict={self.strict}, "
                                      f"min_exclusive={self.min_exclusive}, max_exclusive={self.max_exclusive}{']'}")
        else:
            return values
        
    def _validate_list(self, values: List[ConversionTargetType]) -> bool:
        return self._limits(values=values) and self.validate(values=values)

    def _limits(self, values: List[ConversionTargetType]) -> bool:
        # check strict count
        if self.strict != None:
            return len(values) == self.strict
        
        # check limits
        within_limits = True
        if self.min != None:
            within_limits = within_limits and (\
                (self.min_exclusive and len(values) > self.min) or \
                (not self.min_exclusive and len(values) >= self.min))
            
        if self.max != None:
            within_limits = within_limits and (\
                (self.max_exclusive and len(values) < self.max) or \
                (not self.max_exclusive and len(values) <= self.max))
            
        return within_limits

    def validate(self, values: List[ConversionTargetType]) -> bool:
        """Custom list validation function, override in subclasses
        
        If you need more complex list validation, derive a subclass from ListValidator
        and implement "validate".
        """
        return True

    def specify(self) -> str:
        """Construct a specification string that include the set list limits
        
        You may override this to give users more information about your custom
        list validation routines in the config specification string
        """
        
        # check strict count
        if self.strict != None:
            return f" list must have len = {self.strict}"
        
        # check limits
        elif self.min != None and self.max == None:
            bound: str = ">="
            if self.min_exclusive:
                bound = ">"
            return f" list must have len {bound} {self.min}"
            
        elif self.max != None and self.min == None:
            bound: str = "<="
            if self.max_exclusive:
                bound = "<"
            return f" list must have len {bound} {self.max}"
            pass

        elif self.max != None and self.min != None:
            lower_bound: str = "["
            if self.min_exclusive:
                lower_bound = "("

            upper_bound: str = "]"
            if self.max_exclusive:
                upper_bound = ")"
            
            return f" list must have len in {lower_bound}{self.min}, {self.max}{upper_bound} "
        else:
            return ""



