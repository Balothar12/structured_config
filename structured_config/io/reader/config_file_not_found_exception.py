
from pathlib import Path

class ConfigFileNotFoundException(Exception):

    def __init__(self, file: Path):
        super().__init__(f"Config file {str(file)} not found")