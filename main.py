import asyncio
import pathlib
import tomllib
from typing import cast
import sys

from fire import Fire

from news2discord import News2Discord
from news2discord.models.config import ConfigModel

THIS_DIR = pathlib.Path(__file__).parent
CONFIG_FILE_PATH = THIS_DIR / "config" / "config.toml"


def get_config() -> ConfigModel:
    try:
        with open(CONFIG_FILE_PATH, "rb") as f:
            data = tomllib.load(f)
        return cast(ConfigModel, data)
    except FileNotFoundError:
        print(f"設定ファイルが見つかりません: {CONFIG_FILE_PATH}")
        print(
            "config/example.config.tomlをconfig/config.tomlにコピーして設定してください。"
        )
        sys.exit(1)
    except tomllib.TOMLDecodeError as e:
        print(f"設定ファイルの形式が正しくありません: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"設定ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)


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
