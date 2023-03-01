
class RequiredValueNotFoundException(Exception):

    def __init__(self, value_name: str):
        super().__init__(f"Required config value {value_name} is missing")