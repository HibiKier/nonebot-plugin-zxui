import re

import cattrs
from fastapi import Query
from zhenxun_utils.enum import BlockType, PluginType

from .....models.plugin_info import PluginInfo as DbPluginInfo
from .model import PluginConfig, PluginDetail, PluginInfo, UpdatePlugin


class ApiDataSource:
    @classmethod
    async def get_plugin_list(
        cls, plugin_type: list[PluginType] = Query(None), menu_type: str | None = None
    ) -> list[PluginInfo]:
        """获取插件列表

        参数:
            plugin_type: 插件类型.
            menu_type: 菜单类型.

        返回:
            list[PluginInfo]: 插件数据列表
        """
        plugin_list: list[PluginInfo] = []
        query = DbPluginInfo
        if plugin_type:
            query = query.filter(plugin_type__in=plugin_type, load_status=True)
        if menu_type:
            query = query.filter(menu_type=menu_type, load_status=True)
        plugins = await query.all()
        for plugin in plugins:
            plugin_info = PluginInfo(
                module=plugin.module,
                plugin_name=plugin.name,
                default_status=plugin.default_status,
                limit_superuser=plugin.limit_superuser,
                cost_gold=plugin.cost_gold,
                menu_type=plugin.menu_type,
                version=plugin.version or "0",
                level=plugin.level,
                status=plugin.status,
                author=plugin.author,
            )
            plugin_list.append(plugin_info)
        return plugin_list

    @classmethod
    async def update_plugin(cls, param: UpdatePlugin) -> DbPluginInfo:
        """更新插件数据

        参数:
            param: UpdatePlugin

        返回:
            DbPluginInfo | None: 插件数据
        """
        db_plugin = await DbPluginInfo.get_plugin(module=param.module)
        if not db_plugin:
            raise ValueError("插件不存在")
        db_plugin.default_status = param.default_status
        db_plugin.limit_superuser = param.limit_superuser
        db_plugin.cost_gold = param.cost_gold
        db_plugin.level = param.level
        db_plugin.menu_type = param.menu_type
        db_plugin.block_type = param.block_type
        db_plugin.status = param.block_type != BlockType.ALL
        await db_plugin.save()
        return db_plugin

    @classmethod
    async def get_plugin_detail(cls, module: str) -> PluginDetail:
        """获取插件详情

        参数:
            module: 模块名

        异常:
            ValueError: 插件不存在

        返回:
            PluginDetail: 插件详情数据
        """
        db_plugin = await DbPluginInfo.get_plugin(module=module)
        if not db_plugin:
            raise ValueError("插件不存在")
        return PluginDetail(
            module=module,
            plugin_name=db_plugin.name,
            default_status=db_plugin.default_status,
            limit_superuser=db_plugin.limit_superuser,
            cost_gold=db_plugin.cost_gold,
            menu_type=db_plugin.menu_type,
            version=db_plugin.version or "0",
            level=db_plugin.level,
            status=db_plugin.status,
            author=db_plugin.author,
            config_list=[],
            block_type=db_plugin.block_type,
        )
