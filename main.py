import asyncio
import pathlib
import tomllib
from typing import cast
import sys
import os

from dotenv import load_dotenv
from fire import Fire

from news2discord import News2Discord
from news2discord.models.config import ConfigModel

THIS_DIR = pathlib.Path(__file__).parent
CONFIG_FILE_PATH = THIS_DIR / "config" / "config.toml"
ENV_FILE_PATH = THIS_DIR / ".env"


def load_environment():
    """環境変数を読み込む"""
    # .envファイルが存在する場合は読み込み
    if ENV_FILE_PATH.exists():
        load_dotenv(ENV_FILE_PATH)
        print(f"環境変数を読み込みました: {ENV_FILE_PATH}")
    else:
        print(f".envファイルが見つかりません: {ENV_FILE_PATH}")
        print("env.exampleを.envにコピーして設定してください。")

    # 必須環境変数の確認
    if not os.getenv("OPENAI_API_KEY"):
        print("警告: OPENAI_API_KEYが設定されていません")
        print("環境変数または.envファイルで設定してください")


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
    # 環境変数を読み込み
    load_environment()

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
