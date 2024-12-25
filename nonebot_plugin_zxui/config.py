from pathlib import Path

import nonebot
from pydantic import BaseModel

DEFAULT_DATA_PATH = Path() / "data" / "zxui" / "zxpm"


class Config(BaseModel):
    zxui_db_url: str = ""
    """数据库连接地址"""

    zxui_data_path: str | Path | None = None
    """数据存储路径"""

    zxui_username: str
    """用户名"""

    zxui_password: str
    """密码"""

    zxui_enable_chat_history: bool = True
    """是否开启消息存储"""

    zxui_enable_call_history: bool = True
    """是否开启调用记录存储"""

    zxpm_data_path: str | Path = str(DEFAULT_DATA_PATH.absolute())
    """数据存储路径"""
    zxpm_notice_info_cd: int = 300
    """群/用户权限检测等各种检测提示信息cd，为0时不提醒"""
    zxpm_ban_reply: str = "才不会给你发消息."
    """用户被ban时回复消息，为空时不回复"""
    zxpm_ban_level: int = 5
    """使用ban功能的对应权限"""
    zxpm_switch_level: int = 1
    """群组插件开关管理对应权限"""
    zxpm_admin_default_auth: int = 5
    """群组管理员默认权限"""


config = nonebot.get_plugin_config(Config)

if not config.zxui_data_path:
    config.zxui_data_path = Path() / "data" / "zxui"

if isinstance(config.zxui_data_path, str):
    config.zxui_data_path = Path(config.zxui_data_path)

config.zxui_data_path.mkdir(parents=True, exist_ok=True)

if not config.zxui_db_url:
    db_path = config.zxui_data_path / "db" / "zhenxun.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    config.zxui_db_url = f"sqlite:{db_path.absolute()}"

DATA_PATH = config.zxui_data_path

SQL_TYPE = config.zxui_db_url.split(":")[0]
