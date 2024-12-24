from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

import nonebot
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from zhenxun_db_client import client_db


from .config import Config
from .config import config as PluginConfig
from .web_ui import *  # noqa: F403

driver = nonebot.get_driver()

__plugin_meta__ = PluginMetadata(
    name="小真寻的WebUi",
    description="小真寻的WebUi",
    usage=r"""
    无
    """,
    type="application",
    homepage="https://github.com/HibiKier/nonebot-plugin-zxui",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    extra={"author": "HibiKier"},
)


@driver.on_startup
async def _():
    await client_db(PluginConfig.zxui_db_url)
