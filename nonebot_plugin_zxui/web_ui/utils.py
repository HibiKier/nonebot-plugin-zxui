import contextlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psutil
import ujson as json
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from nonebot.utils import run_sync

from ..config import DATA_PATH, config
from .base_model import SystemFolderSize, SystemStatus, User

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

SECRET_FILE = DATA_PATH / "secret.txt"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

token_file = DATA_PATH / "token.json"
token_file.parent.mkdir(parents=True, exist_ok=True)
token_data = {"token": []}
if token_file.exists():
    with contextlib.suppress(json.JSONDecodeError):
        token_data = json.load(open(token_file, encoding="utf8"))

if not SECRET_FILE.exists():
    with SECRET_FILE.open("w", encoding="utf8") as f:
        f.write(secrets.token_urlsafe(32))


def get_user(uname: str) -> User | None:
    """获取账号密码

    参数:
        uname: uname

    返回:
        Optional[User]: 用户信息
    """
    username = config.zxui_username
    password = config.zxui_password
    if username and password and uname == username:
        return User(username=username, password=password)


def create_token(user: User, expires_delta: timedelta | None = None):
    """创建token

    参数:
        user: 用户信息
        expires_delta: 过期时间.
    """
    with SECRET_FILE.open(encoding="utf8") as f:
        secret = f.read().strip()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    return jwt.encode(
        claims={"sub": user.username, "exp": expire},
        key=secret,
        algorithm=ALGORITHM,
    )


def authentication():
    """权限验证

    异常:
        JWTError: JWTError
        HTTPException: HTTPException
    """

    # if token not in token_data["token"]:
    def inner(token: str = Depends(oauth2_scheme)):
        try:
            with SECRET_FILE.open(encoding="utf8") as f:
                secret = f.read().strip()
            payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
            username, _ = payload.get("sub"), payload.get("exp")
            user = get_user(username)  # type: ignore
            if user is None:
                raise JWTError
        except JWTError:
            raise HTTPException(
                status_code=400, detail="登录验证失败或已失效, 踢出房间!"
            )

    return Depends(inner)


def _get_dir_size(dir_path: Path) -> float:
    """获取文件夹大小

    参数:
        dir_path: 文件夹路径
    """
    return sum(
        sum(os.path.getsize(os.path.join(root, name)) for name in files)
        for root, dirs, files in os.walk(dir_path)
    )


@run_sync
def get_system_status() -> SystemStatus:
    """获取系统信息等"""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    return SystemStatus(
        cpu=cpu,
        memory=memory,
        disk=disk,
        check_time=datetime.now().replace(microsecond=0),
    )


@run_sync
def get_system_disk(
    full_path: str | None,
) -> list[SystemFolderSize]:
    """获取资源文件大小等"""
    base_path = Path(full_path) if full_path else Path()
    other_size = 0
    data_list = []
    for file in os.listdir(base_path):
        f = base_path / file
        if f.is_dir():
            size = _get_dir_size(f) / 1024 / 1024
            data_list.append(
                SystemFolderSize(name=file, size=size, full_path=str(f), is_dir=True)
            )
        else:
            other_size += f.stat().st_size / 1024 / 1024
    if other_size:
        data_list.append(
            SystemFolderSize(
                name="other_file", size=other_size, full_path=full_path, is_dir=False
            )
        )
    return data_list
