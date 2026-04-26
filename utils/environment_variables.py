import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EnvironmentVariables:
    __env_var_name: str = "INKPULL_CONFIG"
    CONFIG_PATH: Path | None = None

    def __post_init__(self):
        raw_value = os.getenv(self.__env_var_name)
        if raw_value is None:
            return

        path = Path(raw_value)
        if not path.exists():
            raise FileNotFoundError("File not found")

        if not path.is_file():
            raise ValueError("Provided path is not a file")

        if path.suffix != ".json":
            raise ValueError("Provided path is not a json file")

        object.__setattr__(self, "CONFIG_PATH", path)


env = EnvironmentVariables()
