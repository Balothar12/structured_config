
from structured_config.typedefs import ConfigObjectType
from structured_config.io.reader.config_file_not_found_exception import ConfigFileNotFoundException
from pathlib import Path

class ConfigReaderBase:

    def check_file(self, file: Path):
        if not file.resolve().exists():
            raise ConfigFileNotFoundException(file=file.resolve())

    def read(self) -> ConfigObjectType:
        raise NotImplementedError()