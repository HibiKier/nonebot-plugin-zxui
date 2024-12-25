import asyncio

import nonebot
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nonebot.log import default_filter, default_format
from zhenxun_utils.log import logger, logger_

from .api.logs import router as ws_log_routes
from .api.logs.log_manager import LOG_STORAGE
from .api.menu import router as menu_router
from .api.tabs.dashboard import router as dashboard_router
from .api.tabs.database import router as database_router
from .api.tabs.main import router as main_router
from .api.tabs.main import ws_router as status_routes
from .api.tabs.manage import router as manage_router
from .api.tabs.manage.chat import ws_router as chat_routes
from .api.tabs.plugin_manage import router as plugin_router
from .api.tabs.system import router as system_router
from .auth import router as auth_router
from .public import init_public

driver = nonebot.get_driver()


BaseApiRouter = APIRouter(prefix="/zhenxun/api")


BaseApiRouter.include_router(auth_router)
BaseApiRouter.include_router(dashboard_router)
BaseApiRouter.include_router(main_router)
BaseApiRouter.include_router(manage_router)
BaseApiRouter.include_router(database_router)
BaseApiRouter.include_router(plugin_router)
BaseApiRouter.include_router(system_router)
BaseApiRouter.include_router(menu_router)


WsApiRouter = APIRouter(prefix="/zhenxun/socket")

WsApiRouter.include_router(ws_log_routes)
WsApiRouter.include_router(status_routes)
WsApiRouter.include_router(chat_routes)


@driver.on_startup
async def _():
    try:

        async def log_sink(message: str):
            loop = None
            if not loop:
                try:
                    loop = asyncio.get_running_loop()
                except Exception as e:
                    logger.warning("Web Ui log_sink", e=e)
            if not loop:
                loop = asyncio.new_event_loop()
            loop.create_task(LOG_STORAGE.add(message.rstrip("\n")))  # noqa: RUF006

        logger_.add(
            log_sink, colorize=True, filter=default_filter, format=default_format
        )

        app: FastAPI = nonebot.get_app()
        app.include_router(BaseApiRouter)
        app.include_router(WsApiRouter)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        await init_public(app)
        logger.info("<g>API启动成功</g>", "WebUi")
    except Exception as e:
        logger.error("<g>API启动失败</g>", "WebUi", e=e)
