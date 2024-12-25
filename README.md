<div align=center>

<img width="250" height="312" src="https://github.com/HibiKier/nonebot-plugin-zxui/blob/main/docs_image/tt.jpg"/>

</div>

<div align="center">

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# nonebot-plugin-zxui

_✨ 基于 [NoneBot2](https://github.com/nonebot/nonebot2) 的 小真寻WebUi API实现 ✨_

![python](https://img.shields.io/badge/python-v3.10%2B-blue)
![nonebot](https://img.shields.io/badge/nonebot-v2.1.3-yellow)
![onebot](https://img.shields.io/badge/onebot-v11-black)
[![license](https://img.shields.io/badge/license-AGPL3.0-FE7D37)](https://github.com/HibiKier/zhenxun_bot/blob/main/LICENSE)

</div>

## 📖 介绍

[小真寻](https://github.com/HibiKier/zhenxun_bot)具象化了。  

内置 [ZXPM插件管理](https://github.com/HibiKier/nonebot-plugin-zxpm)（帮助看这个readme）

> [!NOTE]
>
> <div align="center"><b>小真寻也很可爱呀，也会很喜欢你！</b></div>
>
> <div align="center">
> <img width="235" height="235" src="https://github.com/HibiKier/nonebot-plugin-zxwb/blob/main/docs_image/tt3.png"/>
> <img width="235" height="235" src="https://github.com/HibiKier/nonebot-plugin-zxwb/blob/main/docs_image/tt1.png"/>
> <img width="235" height="235" src="https://github.com/HibiKier/nonebot-plugin-zxwb/blob/main/docs_image/tt2.png"/>
> </div>

## 💿 安装

```python
pip install nonebot-plugin-zxui
```

```python
nb plugin install nonebot-plugin-zxui
```

### ZXUI

| 配置                    | 类型 |            默认值             | 说明                                                             |
| :---------------------- | :--: | :---------------------------: | ---------------------------------------------------------------- |       
| zxui_data_path          | str  |           data/zxui           | 数据存储路径
|zxui_db_url| str| '' | 数据库地址 URL，默认为 sqlite,存储路径在`zxpm_data_path`|
| zxui_username          | str  |                      | 必填项，登录用户名
| zxui_password          | str  |                      | 必填项，登录密码
| zxui_enable_chat_history          | bool  | 开启消息存储                    | 
| zxui_enable_call_history          | bool  | 开启调用记录存储                    |


### ZXPM

| 配置                    | 类型 |            默认值             | 说明                                                             |
| :---------------------- | :--: | :---------------------------: | ---------------------------------------------------------------- |    
| zxpm_data_path          | str  |           data/zxui/zxpm           | 数据存储路径                                                     |
| zxpm_db_url             | str  | (`zxpm_data_path`)/db/zxpm.db | 数据库地址 URL，默认为 sqlite,存储路径在`zxpm_data_path`下       |
| zxpm_notice_info_cd     | int  |              300              | 群/用户权限检测等各种检测提示信息 cd，为 0 时或永久 ban 时不提醒 |
| zxpm_ban_reply          | str  |       才不会给你发消息.       | 用户被 ban 时回复消息，为空时不回复                              |
| zxpm_ban_level          | int  |               5               | 使用 ban 功能的对应权限                                          |
| zxpm_switch_level       | int  |               1               | 使用开关功能的对应权限                                           |
| zxpm_admin_default_auth | int  |               5               | 群组管理员默认权限                                               |
| zxpm_limit_superuser               | bool  |           False            | 是否限制超级用户     


## 🎁 后台示例图

<div align="center">

![x](https://raw.githubusercontent.com/HibiKier/zhenxun_bot_zxui/main/docs_image/0.png)
![x](https://raw.githubusercontent.com/HibiKier/zhenxun_bot_zxui/main/docs_image/1.png)
![x](https://raw.githubusercontent.com/HibiKier/zhenxun_bot_zxui/main/docs_image/2.png)
![x](https://raw.githubusercontent.com/HibiKier/zhenxun_bot_zxui/main/docs_image/3.png)
![x](https://raw.githubusercontent.com/HibiKier/zhenxun_bot_zxui/main/docs_image/4.png)
![x](https://raw.githubusercontent.com/HibiKier/zhenxun_bot_zxui/main/docs_image/5.png)
![x](https://raw.githubusercontent.com/HibiKier/zhenxun_bot_zxui/main/docs_image/6.png)
![x](https://raw.githubusercontent.com/HibiKier/zhenxun_bot_zxui/main/docs_image/7.png)

</div>

## ❤ 感谢

- 可爱的小真寻 Bot [`zhenxun_bot`](https://github.com/HibiKier/zhenxun_bot): 我谢我自己，桀桀桀
