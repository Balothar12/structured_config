
from structured_config.io.reader.config_reader_base import ConfigReaderBase, ConfigObjectType
from pathlib import Path
import json

class JsonReader(ConfigReaderBase):

    def __init__(self, file: str):
        self.file: Path = Path(file).resolve()
        self.check_file(file=self.file)

    def read(self) -> ConfigObjectType:
        # 
        with open(file=self.file, mode="r") as json_file:
            # load the json data
            json_data: ConfigObjectType = json.load(json_file)
            return json_data
