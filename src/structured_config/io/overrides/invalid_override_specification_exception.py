
class InvalidOverrideSpecificationException(Exception):

    def __init__(self, reason: str):
        super().__init__(f"Invalid override specification: {reason}")