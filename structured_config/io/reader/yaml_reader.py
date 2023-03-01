
from structured_config.io.reader.config_reader_base import ConfigReaderBase, ConfigObjectType
from pathlib import Path
import yaml

class YamlReader(ConfigReaderBase):

    def __init__(self, file: str):
        self.file: Path = Path(file).resolve()
        self.check_file(file=self.file)

    def read(self) -> ConfigObjectType:
        # open the file
        with open(file=self.file, mode="r") as yaml_file:
            yaml_data: ConfigObjectType = yaml.safe_load(yaml_file)
            return yaml_data
