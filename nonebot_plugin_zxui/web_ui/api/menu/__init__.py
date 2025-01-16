from fastapi import APIRouter
from fastapi.responses import JSONResponse
from nonebot import logger

from ...base_model import Result
from ...utils import authentication
from .data_source import menu_manage
from .model import MenuData

router = APIRouter(prefix="/menu")


@router.get(
    "/get_menus",
    dependencies=[authentication()],
    response_model=Result[MenuData],
    response_class=JSONResponse,
    deprecated="获取菜单列表",  # type: ignore
)
async def _() -> Result[MenuData]:
    try:
        return Result.ok(menu_manage.get_menus(), "拿到菜单了哦！")
    except Exception as e:
        logger.error(f"WebUi {router.prefix}/get_menus 调用错误 {type(e)}:{e}")
        return Result.fail(f"发生了一点错误捏 {type(e)}: {e}")
