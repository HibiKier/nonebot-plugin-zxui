from pathlib import Path

import nonebot
from pydantic import BaseModel


class Config(BaseModel):
    zxui_db_url: str = ""
    """数据库连接地址"""

    zxui_path: str | Path | None = None
    """数据存储路径"""

    zxui_username: str
    """用户名"""

    zxui_password: str
    """密码"""


config = nonebot.get_plugin_config(Config)

if not config.zxui_path:
    config.zxui_path = Path() / "data" / "zxui"

if isinstance(config.zxui_path, str):
    config.zxui_path = Path(config.zxui_path)

config.zxui_path.mkdir(parents=True, exist_ok=True)

if not config.zxui_db_url:
    db_path = config.zxui_path / "db" / "zhenxun.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    config.zxui_db_url = f"sqlite:{db_path.absolute()}"

DATA_PATH = config.zxui_path

SQL_TYPE = config.zxui_db_url.split(":")[0]
