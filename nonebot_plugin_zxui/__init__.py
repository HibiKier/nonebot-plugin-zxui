import nonebot
from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from zhenxun_db_client import client_db

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")
require("nonebot_plugin_uninfo")

from zhenxun_utils.enum import PluginType

driver = nonebot.get_driver()


@driver.on_startup
async def _():
    await client_db(PluginConfig.zxui_db_url)


from .config import Config  # noqa: E402
from .config import config as PluginConfig  # noqa: E402
from .stat import *  # noqa: E402, F403
from .web_ui import *  # noqa: E402, F403
from .zxpm import *  # noqa: E402, F403

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
