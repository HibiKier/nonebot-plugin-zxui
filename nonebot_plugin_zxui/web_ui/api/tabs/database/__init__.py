import nonebot
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from nonebot import logger
from nonebot.drivers import Driver
from tortoise import Tortoise

from .....config import SQL_TYPE
from .....models.plugin_info import PluginInfo
from ....base_model import BaseResultModel, QueryModel, Result
from ....utils import authentication
from .data_source import ApiDataSource, type2sql
from .models.model import Column, SqlText
from .models.sql_log import SqlLog

router = APIRouter(prefix="/database")


driver: Driver = nonebot.get_driver()


@driver.on_startup
async def _():
    if ApiDataSource.SQL_DICT:
        result = await PluginInfo.filter(
            module__in=ApiDataSource.SQL_DICT.keys()
        ).values_list("module", "name")
        module2name = {r[0]: r[1] for r in result}
        for s in ApiDataSource.SQL_DICT:
            module = ApiDataSource.SQL_DICT[s].module
            ApiDataSource.SQL_DICT[s].name = module2name.get(module, module)


@router.get(
    "/get_table_list",
    dependencies=[authentication()],
    response_model=Result[list[dict]],
    response_class=JSONResponse,
    description="获取数据库表",
)
async def _() -> Result[list[dict]]:
    try:
        db = Tortoise.get_connection("default")
        query = await db.execute_query_dict(type2sql[SQL_TYPE])
        return Result.ok(query)
    except Exception as e:
        logger.error(f"WebUi {router.prefix}/get_table_list 调用错误 {type(e)}:{e}")
        return Result.fail(f"发生了一点错误捏 {type(e)}: {e}")


@router.get(
    "/get_table_column",
    dependencies=[authentication()],
    response_model=Result[list[Column]],
    response_class=JSONResponse,
    description="获取表字段",
)
async def _(table_name: str) -> Result[list[Column]]:
    try:
        return Result.ok(
            await ApiDataSource.get_table_column(table_name), "拿到信息啦!"
        )
    except Exception as e:
        logger.error(f"WebUi {router.prefix}/get_table_column 调用错误 {type(e)}:{e}")
        return Result.fail(f"发生了一点错误捏 {type(e)}: {e}")


@router.post(
    "/exec_sql",
    dependencies=[authentication()],
    response_model=Result[list[dict]],
    response_class=JSONResponse,
    description="执行sql",
)
async def _(sql: SqlText, request: Request) -> Result[list[dict]]:
    ip = request.client.host if request.client else "unknown"
    try:
        if sql.sql.lower().startswith("select"):
            db = Tortoise.get_connection("default")
            res = await db.execute_query_dict(sql.sql)
            await SqlLog.add(ip or "0.0.0.0", sql.sql, "")
            return Result.ok(res, "执行成功啦!")
        else:
            result = await PluginInfo.raw(sql.sql)
            await SqlLog.add(ip or "0.0.0.0", sql.sql, str(result))
            return Result.ok(info="执行成功啦!")
    except Exception as e:
        logger.error(f"WebUi {router.prefix}/exec_sql 调用错误 {type(e)}:{e}")
        await SqlLog.add(ip or "0.0.0.0", sql.sql, str(e), False)
        return Result.warning_(f"sql执行错误: {e}")


@router.post(
    "/get_sql_log",
    dependencies=[authentication()],
    response_model=Result[BaseResultModel],
    response_class=JSONResponse,
    description="sql日志列表",
)
async def _(query: QueryModel) -> Result[BaseResultModel]:
    try:
        total = await SqlLog.all().count()
        if total % query.size:
            total += 1
        data = (
            await SqlLog.all()
            .order_by("-id")
            .offset((query.index - 1) * query.size)
            .limit(query.size)
        )
        return Result.ok(BaseResultModel(total=total, data=data))
    except Exception as e:
        logger.error(f"WebUi {router.prefix}/get_sql_log 调用错误 {type(e)}:{e}")
        return Result.fail(f"发生了一点错误捏 {type(e)}: {e}")
