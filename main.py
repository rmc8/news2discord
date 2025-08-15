import asyncio
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


async def _proc_async(offset: int = 1):
    config = get_config()
    n2d = News2Discord(config, offset)
    await n2d.run()


def proc(offset: int = 1):
    """非同期処理を実行するラッパー関数"""
    asyncio.run(_proc_async(offset))


def main():
    Fire(proc)


if __name__ == "__main__":
    main()
