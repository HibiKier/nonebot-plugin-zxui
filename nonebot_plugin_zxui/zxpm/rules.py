from nonebot.adapters import Bot, Event
from nonebot.internal.rule import Rule
from nonebot.permission import SUPERUSER
from nonebot_plugin_session import EventSession, SessionLevel

from ..models.level_user import LevelUser


def ensure_group(session: EventSession) -> bool:
    """
    是否在群聊中

    参数:
        session: session

    返回:
        bool: bool
    """
    return session.level in [SessionLevel.LEVEL2, SessionLevel.LEVEL3]


def admin_check(a: int | None = None) -> Rule:
    """
    管理员权限等级检查

    参数:
        a: 权限等级或 配置项 module
        key: 配置项 key.

    返回:
        Rule: Rule
    """

    async def _rule(bot: Bot, event: Event, session: EventSession) -> bool:
        if await SUPERUSER(bot, event):
            return True
        if session.id1 and session.id2:
            level = a
            if level is not None:
                return bool(
                    await LevelUser.check_level(session.id1, session.id2, int(level))
                )
        return False

    return Rule(_rule)


def notice_rule(event_type: type | list[type]) -> Rule:
    """
    Notice限制

    参数:
        event_type: Event类型

    返回:
        Rule: Rule
    """

    async def _rule(event: Event) -> bool:
        if isinstance(event_type, list):
            for et in event_type:
                if isinstance(event, et):
                    return True
        else:
            return isinstance(event, event_type)
        return False

    return Rule(_rule)
