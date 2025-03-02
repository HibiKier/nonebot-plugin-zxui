import nonebot
from nonebot import require

require("nonebot_plugin_localstore")
require("nonebot_plugin_alconna")
require("nonebot_plugin_session")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_apscheduler")

from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from zhenxun_db_client import client_db
from zhenxun_utils.enum import PluginType

from .config import Config
from .config import config as PluginConfig
from .stat import *  # noqa: F403
from .web_ui import *  # noqa: F403
from .zxpm import *  # noqa: F403

driver = nonebot.get_driver()


@driver.on_startup
async def _():
    await client_db(PluginConfig.zxui_db_url)


__plugin_meta__ = PluginMetadata(
    name="小真寻的WebUi",
    description="小真寻的WebUi",
    usage="",
    type="application",
    homepage="https://github.com/HibiKier/nonebot-plugin-zxui",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna",
        "nonebot_plugin_uninfo",
        "nonebot_plugin_session",
    ),
    extra={"author": "HibiKier", "plugin_type": PluginType.HIDDEN},
)
