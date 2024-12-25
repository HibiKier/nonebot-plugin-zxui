from datetime import datetime

from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.message import run_postprocessor
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_uninfo import Uninfo
from zhenxun_utils.enum import PluginType
from zhenxun_utils.log import logger

from ...config import config
from ...models.plugin_info import PluginInfo
from ...models.statistics import Statistics
from ...zxpm.extra import PluginExtraData

TEMP_LIST = []

__plugin_meta__ = PluginMetadata(
    name="功能调用统计",
    description="功能调用统计",
    usage="""""".strip(),
    extra=PluginExtraData(
        author="HibiKier", version="0.1", plugin_type=PluginType.HIDDEN
    ).dict(),
)


@run_postprocessor
async def _(
    matcher: Matcher,
    exception: Exception | None,
    bot: Bot,
    session: Uninfo,
    event: Event,
):
    if getattr(event, "sub_type") == "poke":
        return
    if not config.zxui_enable_call_history:
        return
    if matcher.plugin:
        plugin = await PluginInfo.get_plugin(module_path=matcher.plugin.module_name)
        plugin_type = plugin.plugin_type if plugin else None
        if plugin_type == PluginType.NORMAL:
            logger.debug(f"提交调用记录: {matcher.plugin_name}...", session=session)
            TEMP_LIST.append(
                Statistics(
                    user_id=session.user.id,
                    group_id=session.group.id if session.group else None,
                    plugin_name=matcher.plugin_name,
                    create_time=datetime.now(),
                    bot_id=bot.self_id,
                )
            )


@scheduler.scheduled_job(
    "interval",
    minutes=1,
)
async def _():
    try:
        call_list = TEMP_LIST.copy()
        TEMP_LIST.clear()
        if call_list:
            await Statistics.bulk_create(call_list)
        logger.debug(f"批量添加调用记录 {len(call_list)} 条", "定时任务")
    except Exception as e:
        logger.error("定时批量添加调用记录", "定时任务", e=e)
