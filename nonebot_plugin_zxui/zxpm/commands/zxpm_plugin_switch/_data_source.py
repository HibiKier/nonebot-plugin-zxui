from zhenxun_utils._image_template import BuildImage, ImageTemplate, RowStyle
from zhenxun_utils.enum import BlockType, PluginType

from ....models.group_console import GroupConsole
from ....models.plugin_info import PluginInfo


class GroupInfoNotFound(Exception):
    """
    群组未找到
    """

    pass


def plugin_row_style(column: str, text: str) -> RowStyle:
    """被动技能文本风格

    参数:
        column: 表头
        text: 文本内容

    返回:
        RowStyle: RowStyle
    """
    style = RowStyle()
    if (column == "全局状态" and text == "开启") or (
        column != "全局状态" and column == "加载状态" and text == "SUCCESS"
    ):
        style.font_color = "#67C23A"
    elif column in {"全局状态", "加载状态"}:
        style.font_color = "#F56C6C"
    return style


async def build_plugin() -> BuildImage:
    column_name = [
        "ID",
        "模块",
        "名称",
        "全局状态",
        "禁用类型",
        "加载状态",
        "菜单分类",
        "作者",
        "版本",
        "金币花费",
    ]
    plugin_list = await PluginInfo.filter(plugin_type__not=PluginType.HIDDEN).all()
    column_data = [
        [
            plugin.id,
            plugin.module,
            plugin.name,
            "开启" if plugin.status else "关闭",
            plugin.block_type,
            "SUCCESS" if plugin.load_status else "ERROR",
            plugin.menu_type,
            plugin.author,
            plugin.version,
            plugin.cost_gold,
        ]
        for plugin in plugin_list
    ]
    return await ImageTemplate.table_page(
        "Plugin",
        "插件状态",
        column_name,
        column_data,
        text_style=plugin_row_style,
    )


def task_row_style(column: str, text: str) -> RowStyle:
    """被动技能文本风格

    参数:
        column: 表头
        text: 文本内容

    返回:
        RowStyle: RowStyle
    """
    style = RowStyle()
    if column in {"群组状态", "全局状态"}:
        style.font_color = "#67C23A" if text == "开启" else "#F56C6C"
    return style


class PluginManage:
    @classmethod
    async def set_default_status(cls, plugin_name: str, status: bool) -> str:
        """设置插件进群默认状态

        参数:
            plugin_name: 插件名称
            status: 状态

        返回:
            str: 返回信息
        """
        if plugin_name.isdigit():
            plugin = await PluginInfo.get_or_none(id=int(plugin_name))
        else:
            plugin = await PluginInfo.get_or_none(
                name=plugin_name, load_status=True, plugin_type__not=PluginType.PARENT
            )
        if plugin:
            plugin.default_status = status
            await plugin.save(update_fields=["default_status"])
            status_text = "开启" if status else "关闭"
            return f"成功将 {plugin.name} 进群默认状态修改为: {status_text}"
        return "没有找到这个功能喔..."

    @classmethod
    async def set_all_plugin_status(
        cls, status: bool, is_default: bool = False, group_id: str | None = None
    ) -> str:
        """修改所有插件状态

        参数:
            status: 状态
            is_default: 是否进群默认.
            group_id: 指定群组id.

        返回:
            str: 返回信息
        """
        if is_default:
            await PluginInfo.filter(plugin_type=PluginType.NORMAL).update(
                default_status=status
            )
            return f'成功将所有功能进群默认状态修改为: {"开启" if status else "关闭"}'
        if group_id:
            if group := await GroupConsole.get_or_none(
                group_id=group_id, channel_id__isnull=True
            ):
                module_list = await PluginInfo.filter(
                    plugin_type=PluginType.NORMAL
                ).values_list("module", flat=True)
                if status:
                    for module in module_list:
                        group.block_plugin = group.block_plugin.replace(
                            f"<{module},", ""
                        )
                else:
                    module_list = [f"<{module}" for module in module_list]
                    group.block_plugin = ",".join(module_list) + ","  # type: ignore
                await group.save(update_fields=["block_plugin"])
                return f'成功将此群组所有功能状态修改为: {"开启" if status else "关闭"}'
            return "获取群组失败..."
        await PluginInfo.filter(plugin_type=PluginType.NORMAL).update(
            status=status, block_type=None if status else BlockType.ALL
        )
        return f'成功将所有功能全局状态修改为: {"开启" if status else "关闭"}'

    @classmethod
    async def is_wake(cls, group_id: str) -> bool:
        """是否醒来

        参数:
            group_id: 群组id

        返回:
            bool: 是否醒来
        """
        if c := await GroupConsole.get_or_none(
            group_id=group_id, channel_id__isnull=True
        ):
            return c.status
        return False

    @classmethod
    async def sleep(cls, group_id: str):
        """休眠

        参数:
            group_id: 群组id
        """
        await GroupConsole.filter(group_id=group_id, channel_id__isnull=True).update(
            status=False
        )

    @classmethod
    async def wake(cls, group_id: str):
        """醒来

        参数:
            group_id: 群组id
        """
        await GroupConsole.filter(group_id=group_id, channel_id__isnull=True).update(
            status=True
        )

    @classmethod
    async def block(cls, module: str):
        """禁用

        参数:
            module: 模块名
        """
        await PluginInfo.filter(module=module).update(status=False)

    @classmethod
    async def unblock(cls, module: str):
        """启用

        参数:
            module: 模块名
        """
        await PluginInfo.filter(module=module).update(status=True)

    @classmethod
    async def block_group_plugin(cls, plugin_name: str, group_id: str) -> str:
        """禁用群组插件

        参数:
            plugin_name: 插件名称
            group_id: 群组id

        返回:
            str: 返回信息
        """
        return await cls._change_group_plugin(plugin_name, group_id, False)

    @classmethod
    async def unblock_group_plugin(cls, plugin_name: str, group_id: str) -> str:
        """启用群组插件

        参数:
            plugin_name: 插件名称
            group_id: 群组id

        返回:
            str: 返回信息
        """
        return await cls._change_group_plugin(plugin_name, group_id, True)

    @classmethod
    async def _change_group_plugin(
        cls, plugin_name: str, group_id: str, status: bool
    ) -> str:
        """修改群组插件状态

        参数:
            plugin_name: 插件名称
            group_id: 群组id
            status: 插件状态

        返回:
            str: 返回信息
        """

        if plugin_name.isdigit():
            plugin = await PluginInfo.get_or_none(id=int(plugin_name))
        else:
            plugin = await PluginInfo.get_or_none(
                name=plugin_name, load_status=True, plugin_type__not=PluginType.PARENT
            )
        if plugin:
            status_str = "开启" if status else "关闭"
            if status:
                if await GroupConsole.is_normal_block_plugin(group_id, plugin.module):
                    await GroupConsole.set_unblock_plugin(group_id, plugin.module)
                    return f"已成功{status_str} {plugin.name} 功能!"
            elif not await GroupConsole.is_normal_block_plugin(group_id, plugin.module):
                await GroupConsole.set_block_plugin(group_id, plugin.module)
                return f"已成功{status_str} {plugin.name} 功能!"
            return f"该功能已经{status_str}了喔，不要重复{status_str}..."
        return "没有找到这个功能喔..."

    @classmethod
    async def superuser_block(
        cls, plugin_name: str, block_type: BlockType | None, group_id: str | None
    ) -> str:
        """超级用户禁用插件

        参数:
            plugin_name: 插件名称
            block_type: 禁用类型
            group_id: 群组id

        返回:
            str: 返回信息
        """
        if plugin_name.isdigit():
            plugin = await PluginInfo.get_or_none(id=int(plugin_name))
        else:
            plugin = await PluginInfo.get_or_none(
                name=plugin_name, load_status=True, plugin_type__not=PluginType.PARENT
            )
        if plugin:
            if group_id:
                if not await GroupConsole.is_superuser_block_plugin(
                    group_id, plugin.module
                ):
                    await GroupConsole.set_block_plugin(group_id, plugin.module, True)
                    return f"已成功关闭群组 {group_id} 的 {plugin_name} 功能!"
                return "此群组该功能已被超级用户关闭，不要重复关闭..."
            plugin.block_type = block_type
            plugin.status = not bool(block_type)
            await plugin.save(update_fields=["status", "block_type"])
            if not block_type:
                return f"已成功将 {plugin.name} 全局启用!"
            if block_type == BlockType.ALL:
                return f"已成功将 {plugin.name} 全局关闭!"
            if block_type == BlockType.GROUP:
                return f"已成功将 {plugin.name} 全局群组关闭!"
            if block_type == BlockType.PRIVATE:
                return f"已成功将 {plugin.name} 全局私聊关闭!"
        return "没有找到这个功能喔..."

    @classmethod
    async def superuser_unblock(
        cls, plugin_name: str, block_type: BlockType | None, group_id: str | None
    ) -> str:
        """超级用户开启插件

        参数:
            plugin_name: 插件名称
            block_type: 禁用类型
            group_id: 群组id

        返回:
            str: 返回信息
        """
        if plugin_name.isdigit():
            plugin = await PluginInfo.get_or_none(id=int(plugin_name))
        else:
            plugin = await PluginInfo.get_or_none(
                name=plugin_name, load_status=True, plugin_type__not=PluginType.PARENT
            )
        if plugin:
            if group_id:
                if await GroupConsole.is_superuser_block_plugin(
                    group_id, plugin.module
                ):
                    await GroupConsole.set_unblock_plugin(group_id, plugin.module, True)
                    return f"已成功开启群组 {group_id} 的 {plugin_name} 功能!"
                return "此群组该功能已被超级用户开启，不要重复开启..."
            plugin.block_type = block_type
            plugin.status = not bool(block_type)
            await plugin.save(update_fields=["status", "block_type"])
            if not block_type:
                return f"已成功将 {plugin.name} 全局启用!"
            if block_type == BlockType.ALL:
                return f"已成功将 {plugin.name} 全局开启!"
            if block_type == BlockType.GROUP:
                return f"已成功将 {plugin.name} 全局群组开启!"
            if block_type == BlockType.PRIVATE:
                return f"已成功将 {plugin.name} 全局私聊开启!"
        return "没有找到这个功能喔..."
