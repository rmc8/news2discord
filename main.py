import pathlib
import tomllib
from typing import cast

from fire import Fire

from news2discord import News2Discord
from news2discord.models.config import ConfigModel

THIS_DIR = pathlib.Path(__file__).parent
CONFIG_FILE_PATH = THIS_DIR / "config" / "config.toml"


def get_config() -> ConfigModel:
    with open(CONFIG_FILE_PATH, "rb") as f:
        data = tomllib.load(f)
    return cast(ConfigModel, data)


def proc(offset: int = 1):
    config = get_config()
    n2d = News2Discord(config, offset)
    n2d.run()


def main():
    Fire(proc)


if __name__ == "__main__":
    main()
