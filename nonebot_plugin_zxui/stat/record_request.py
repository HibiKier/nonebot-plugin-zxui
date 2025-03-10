import time

from nonebot import on_message, on_request
from nonebot.adapters.onebot.v11 import (
    ActionFailed,
    FriendRequestEvent,
    GroupRequestEvent,
)
from nonebot.adapters.onebot.v11 import Bot as v11Bot
from nonebot.adapters.onebot.v12 import Bot as v12Bot
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_session import EventSession
from zhenxun_utils.enum import PluginType, RequestHandleType, RequestType
from zhenxun_utils.log import logger

from ..models.fg_request import FgRequest
from ..models.group_console import GroupConsole
from ..zxpm.extra import PluginExtraData

__plugin_meta__ = PluginMetadata(
    name="记录请求",
    description="记录 好友/群组 请求",
    usage="",
    extra=PluginExtraData(
        author="HibiKier",
        version="0.1",
        plugin_type=PluginType.HIDDEN,
    ).dict(),
)


class Timer:
    data: dict[str, float] = {}  # noqa: RUF012

    @classmethod
    def check(cls, uid: int | str):
        return True if uid not in cls.data else time.time() - cls.data[uid] > 5 * 60

    @classmethod
    def clear(cls):
        now = time.time()
        cls.data = {k: v for k, v in cls.data.items() if v - now < 5 * 60}


# TODO: 其他平台请求

friend_req = on_request(priority=5, block=True)
group_req = on_request(priority=5, block=True)
_t = on_message(priority=999, block=False, rule=lambda: False)


@friend_req.handle()
async def _(bot: v12Bot | v11Bot, event: FriendRequestEvent, session: EventSession):
    if event.user_id and Timer.check(event.user_id):
        logger.debug("收录好友请求...", "好友请求", target=event.user_id)
        user = await bot.get_stranger_info(user_id=event.user_id)
        nickname = user["nickname"]
        # sex = user["sex"]
        # age = str(user["age"])
        comment = event.comment
        # 旧请求全部设置为过期
        await FgRequest.filter(
            request_type=RequestType.FRIEND,
            user_id=str(event.user_id),
            handle_type__isnull=True,
        ).update(handle_type=RequestHandleType.EXPIRE)
        await FgRequest.create(
            request_type=RequestType.FRIEND,
            platform=session.platform,
            bot_id=bot.self_id,
            flag=event.flag,
            user_id=event.user_id,
            nickname=nickname,
            comment=comment,
        )
    else:
        logger.debug("好友请求五分钟内重复, 已忽略", "好友请求", target=event.user_id)


@group_req.handle()
async def _(bot: v12Bot | v11Bot, event: GroupRequestEvent, session: EventSession):
    if event.sub_type != "invite":
        return
    if str(event.user_id) in bot.config.superusers:
        try:
            logger.debug(
                "超级用户自动同意加入群聊",
                "群聊请求",
                session=event.user_id,
                target=event.group_id,
            )
            group, _ = await GroupConsole.update_or_create(
                group_id=str(event.group_id),
                defaults={
                    "group_name": "",
                    "max_member_count": 0,
                    "member_count": 0,
                    "group_flag": 1,
                },
            )
            await bot.set_group_add_request(
                flag=event.flag, sub_type="invite", approve=True
            )
            if isinstance(bot, v11Bot):
                group_info = await bot.get_group_info(group_id=event.group_id)
                max_member_count = group_info["max_member_count"]
                member_count = group_info["member_count"]
            else:
                group_info = await bot.get_group_info(group_id=str(event.group_id))
                max_member_count = 0
                member_count = 0
            group.max_member_count = max_member_count
            group.member_count = member_count
            group.group_name = group_info["group_name"]
            await group.save(
                update_fields=["group_name", "max_member_count", "member_count"]
            )
        except ActionFailed as e:
            logger.error(
                "超级用户自动同意加入群聊发生错误",
                "群聊请求",
                session=event.user_id,
                target=event.group_id,
                e=e,
            )
    elif Timer.check(f"{event.user_id}:{event.group_id}"):
        logger.debug(
            f"收录 用户[{event.user_id}] 群聊[{event.group_id}] 群聊请求",
            "群聊请求",
            target=event.group_id,
        )
        # 旧请求全部设置为过期
        await FgRequest.filter(
            request_type=RequestType.GROUP,
            user_id=str(event.user_id),
            group_id=str(event.group_id),
            handle_type__isnull=True,
        ).update(handle_type=RequestHandleType.EXPIRE)
        await FgRequest.create(
            request_type=RequestType.GROUP,
            platform=session.platform,
            bot_id=bot.self_id,
            flag=event.flag,
            user_id=str(event.user_id),
            nickname="",
            group_id=str(event.group_id),
        )
    else:
        logger.debug(
            "群聊请求五分钟内重复, 已忽略",
            "群聊请求",
            target=f"{event.user_id}:{event.group_id}",
        )


@scheduler.scheduled_job(
    "interval",
    minutes=5,
)
async def _():
    Timer.clear()


async def _():
    Timer.clear()
