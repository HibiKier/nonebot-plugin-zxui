import contextlib
from datetime import datetime

import nonebot
from nonebot.adapters import Bot
from nonebot.drivers import Driver
from zhenxun_utils.log import logger
from zhenxun_utils.platform import PlatformUtils

from ..models.bot_connect_log import BotConnectLog
from ..models.bot_console import BotConsole

driver: Driver = nonebot.get_driver()


@driver.on_bot_connect
async def _(bot: Bot):
    logger.debug(f"Bot: {bot.self_id} 建立连接...")
    await BotConnectLog.create(
        bot_id=bot.self_id, platform=bot.adapter, connect_time=datetime.now(), type=1
    )
    if not await BotConsole.exists(bot_id=bot.self_id):
        await BotConsole.create(
            bot_id=bot.self_id, platform=PlatformUtils.get_platform(bot)
        )


@driver.on_bot_disconnect
async def _(bot: Bot):
    logger.debug(f"Bot: {bot.self_id} 断开连接...")
    await BotConnectLog.create(
        bot_id=bot.self_id, platform=bot.adapter, connect_time=datetime.now(), type=0
    )


from .chat_history import *  # noqa: E402, F403
from .statistics import *  # noqa: E402, F403

with contextlib.suppress(ImportError):
    from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent  # noqa: F401

    from .record_request import *  # noqa: F403
