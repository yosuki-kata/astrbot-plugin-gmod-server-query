# -*- coding: utf-8 -*-
"""GMod 服务器查询插件（重制版 v1.0.3）

基于原 v3.3.2 的全部功能彻底重写，采用更清晰的结构与命名。
功能涵盖：别名管理、IP/别名查询、超时控制、消息监听、服务器列表渲染图、可视化配置。

设计要点（参考《插件开发踩坑参考.md》）：
 - html_render 的 options 不用数字 scale，避免云端 T2I 返回 HTTP 422
 - 所有网络 I/O 套超时（asyncio.wait_for + run_in_executor）
 - a2s 返回字段一律 getattr 兜底
 - 玩家列表查询失败不影响主信息
 - html_render 兼容旧版无 options 参数的 TypeError 回退
 - 数据文件路径相对于插件目录，JSON 读写 try/except 兜底
"""

import asyncio
import ipaddress
import json
import os
import a2s
from astrbot.api.all import *
from astrbot.api.event import filter  # 显式导入 filter，避免与 Python 内置 filter 冲突


# ==================== 配置常量 ====================
class Config:
    """配置项默认值集中定义，便于与 _conf_schema.json 核对。"""
    DEFAULT_PORT = 27015        # default_port
    QUERY_TIMEOUT = 5           # query_timeout
    ENABLE_LISTEN = True        # enable_listen
    LISTEN_ONLY_GROUP = True    # listen_only_group
    LISTEN_EXACT_MATCH = True   # listen_exact_match
    RENDER_IMAGE = True         # render_image
    RENDER_KEYWORDS = ["服务器列表", "列表"]  # render_keywords
    RENDER_QUALITY = 92         # render_quality


# ==================== 列表渲染图 HTML 模板（Jinja2） ====================
LIST_TMPL = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: #e6e9f5;
    padding: 28px;
    min-height: 100vh;
}
.container { max-width: 920px; margin: 0 auto; }
.header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 22px;
}
.header h1 { font-size: 26px; }
.badge {
    background: rgba(255,255,255,0.12); color: #b9c2ff;
    padding: 5px 14px; border-radius: 20px; font-size: 14px;
}
.card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 16px;
    backdrop-filter: blur(4px);
}
.card .top { display: flex; align-items: center; justify-content: space-between; }
.card .name { font-size: 18px; font-weight: 600; }
.card .alias { margin-top: 6px; color: #a8b0cc; font-size: 13px; }
.card .alias .addr { color: #7e87a8; }
.card .status { font-size: 20px; font-weight: 700; color: #4ade80; }
.card .status.offline { color: #f87171; }
.card .status .err { font-size: 16px; }
.card .meta { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px; }
.card .tag {
    background: rgba(255,255,255,0.10); color: #cfd3ff;
    border-radius: 6px; padding: 3px 10px; font-size: 12px;
}
.card .tag.blue   { background: rgba(102,126,234,0.25); color: #d5ccff; }
.card .tag.green  { background: rgba(74,222,128,0.18); color: #86efac; }
.card .tag.gray   { background: rgba(255,255,255,0.12); color: #ccc; }
.card .players-list {
    margin-top: 10px; padding-top: 10px;
    border-top: 1px dashed rgba(255,255,255,0.15);
    color: #cfd3ff; font-size: 13px; line-height: 1.5;
}
.card .players-list .label { color: #8b93a7; }
.card .meta .err { color: #f87171; }
.empty { color: #8b93a7; font-size: 15px; text-align: center; padding: 40px 0; }
.footer {
    text-align: right; color: #888; font-size: 12px;
    margin-top: 14px; padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.10);
}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🎮 GMod 服务器列表</h1>
        <span class="badge">共 {{ servers|length }} 台</span>
    </div>

    {% if servers %}
        {% for s in servers %}
        <div class="card">
            <div class="top">
                <div class="name">{{ s.name or s.alias }}</div>
                <div class="status {{ 'offline' if not s.online else '' }}">
                    {% if s.online %}
                        {{ s.players }}<span style="color:#888;font-size:14px;font-weight:400"> / {{ s.max_players }}</span>
                    {% else %}
                        <span class="err">离线</span>
                    {% endif %}
                </div>
            </div>
            <div class="alias">🏷️ {{ s.alias }} 　<span class="addr">{{ s.ip }}:{{ s.port }}</span></div>
            {% if s.online %}
            <div class="meta">
                {% if s.map %}<span class="tag green">🗺️ {{ s.map }}</span>{% endif %}
                {% if s.game %}<span class="tag blue">{{ s.game }}</span>{% endif %}
                {% if s.folder %}<span class="tag gray">{{ s.folder }}</span>{% endif %}
                {% if s.version %}<span class="tag gray">v{{ s.version }}</span>{% endif %}
                {% if s.platform %}
                    <span class="tag {{ 'green' if s.platform == 'l' else 'gray' }}">🖥️ {{ 'Linux' if s.platform == 'l' else 'Windows' }}</span>
                {% endif %}
                {% if s.server_type %}
                    <span class="tag gray">{{ '专用' if s.server_type == 'd' else ('监听' if s.server_type == 'l' else s.server_type) }}</span>
                {% endif %}
                {% if s.bots %}<span class="tag gray">🤖 {{ s.bots }} 机器人</span>{% endif %}
                {% if s.vac is not none %}
                    <span class="tag {{ 'green' if s.vac else 'gray' }}">🛡️ {{ 'VAC' if s.vac else '无VAC' }}</span>
                {% endif %}
            </div>
            {% if s.players_on %}
            <div class="players-list"><span class="label">👥 在线: </span>{{ s.players_on }}</div>
            {% endif %}
            {% else %}
            <div class="meta"><span class="err">{{ s.err }}</span></div>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}
        <div class="empty">📭 暂无已保存的服务器<br><span style="font-size:13px">使用 /gmod-admin add &lt;别名&gt; &lt;IP&gt; [端口] 添加</span></div>
    {% endif %}

    <div class="footer">生成于 {{ time }}</div>
</div>
</body>
</html>
"""


class GModServerQuery(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.servers = {}  # 别名 -> {"ip": str, "port": int}
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "servers.json")
        self._load()

    # ==================== 配置读取 ====================
    def _cfg(self, key, default):
        """安全读取配置项，任何异常都回退到默认值。"""
        try:
            return self.config.get(key, default)
        except Exception:
            return default

    def _default_port(self) -> int:
        try:
            return int(self._cfg("default_port", Config.DEFAULT_PORT))
        except (TypeError, ValueError):
            return Config.DEFAULT_PORT

    def _timeout(self) -> float:
        try:
            return float(self._cfg("query_timeout", Config.QUERY_TIMEOUT))
        except (TypeError, ValueError):
            return Config.QUERY_TIMEOUT

    def _listen_enabled(self) -> bool:
        return bool(self._cfg("enable_listen", Config.ENABLE_LISTEN))

    def _listen_group_only(self) -> bool:
        return bool(self._cfg("listen_only_group", Config.LISTEN_ONLY_GROUP))

    def _exact_match(self) -> bool:
        return bool(self._cfg("listen_exact_match", Config.LISTEN_EXACT_MATCH))

    def _render_enabled(self) -> bool:
        return bool(self._cfg("render_image", Config.RENDER_IMAGE))

    def _render_keywords(self) -> list:
        kw = self._cfg("render_keywords", Config.RENDER_KEYWORDS)
        return kw if isinstance(kw, list) and kw else Config.RENDER_KEYWORDS

    def _render_quality(self) -> int:
        try:
            return max(40, min(100, int(self._cfg("render_quality", Config.RENDER_QUALITY))))
        except (TypeError, ValueError):
            return Config.RENDER_QUALITY

    # ==================== 数据持久化 ====================
    def _load(self):
        """从 servers.json 加载数据。文件缺失或损坏时静默重置。"""
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.servers = data
            else:
                self.servers = {}
        except Exception as e:
            logger.error(f"加载 servers.json 失败: {e}")
            self.servers = {}

    def _save(self):
        """保存数据到 servers.json。"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.servers, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存 servers.json 失败: {e}")

    # ==================== 地址判断 ====================
    @staticmethod
    def _looks_like_address(s: str) -> bool:
        """判断一个字符串是否可能是 IP 或域名地址。"""
        if not s:
            return False
        try:
            ipaddress.ip_address(s)
            return True
        except ValueError:
            pass
        if "." not in s:
            return False
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-")
        return all(ch in allowed for ch in s)

    # ==================== a2s 查询核心 ====================
    async def _query_one(self, alias, ip: str, port: int) -> dict:
        """查询单台服务器信息（a2s.info + a2s.players），返回字典。
        失败时带 online=False 与 err 说明，不影响其他服务器查询。
        """
        base = {"alias": alias, "ip": ip, "port": port}
        try:
            loop = asyncio.get_running_loop()
            info = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: a2s.info((ip, port))),
                timeout=self._timeout(),
            )

            # 玩家列表是附属信息，失败不影响主信息
            players_on = ""
            try:
                ps = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: a2s.players((ip, port))),
                    timeout=self._timeout(),
                )
                if ps:
                    names = []
                    for p in ps:
                        name = getattr(p, "name", "") or ""
                        if name:
                            names.append(name)
                    shown = names[:8]
                    if len(names) > 8:
                        players_on = "、".join(shown) + f" 等{len(names)}人"
                    else:
                        players_on = "、".join(shown)
            except Exception:
                players_on = ""

            base.update({
                "online": True,
                "name": getattr(info, "server_name", "") or "",
                "map": getattr(info, "map_name", "") or "",
                "game": getattr(info, "game", "") or "",
                "folder": getattr(info, "folder", "") or "",
                "version": getattr(info, "version", "") or "",
                "players": getattr(info, "player_count", 0) or 0,
                "max_players": getattr(info, "max_players", 0) or 0,
                "bots": getattr(info, "bots", 0) or 0,
                "server_type": str(getattr(info, "server_type", "") or ""),
                "platform": str(getattr(info, "platform", "") or ""),
                "vac": getattr(info, "vac_enabled", None),
                "players_on": players_on,
            })
        except asyncio.TimeoutError:
            base.update({"online": False, "err": "查询超时"})
        except Exception as e:
            base.update({"online": False, "err": str(e)[:40]})
        return base

    # ==================== 单服务器查询 & 格式化 ====================
    async def _query_server(self, alias, ip: str, port: int) -> str:
        """查询单台服务器并格式化为文本返回。"""
        try:
            info = await self._query_one(alias, ip, port)
        except Exception as e:
            logger.error(f"查询失败 {ip}:{port} - {e}")
            return f"❌ 查询失败 ({ip}:{port}): {e}"

        if not info.get("online"):
            return f"❌ [{alias or ip}] 服务器离线（{info.get('err', '')}）。"

        title = f"[{alias}] " if alias else ""
        name = info.get("name", "") or alias or ""
        text = (
            f"{title}服务器信息:\n"
            f"    名称: {name}\n"
            f"    地图: {info.get('map', '')}\n"
            f"    当前在线: {info.get('players', 0)}/{info.get('max_players', 0)}"
        )
        players_on = info.get("players_on", "") or ""
        if players_on:
            text += f"\n    在线玩家: {players_on}"
        return text

    # ==================== 列表渲染图 ====================
    async def _render_list_image(self) -> str:
        """并发查询所有服务器，将列表渲染为图片，返回图片 URL。"""
        import datetime

        tasks = []
        for alias, srv in self.servers.items():
            tasks.append(self._query_one(alias, srv["ip"], srv["port"]))
        results = await asyncio.gather(*tasks) if tasks else []

        servers_data = []
        for info in results:
            servers_data.append({
                "alias": info["alias"], "ip": info["ip"], "port": info["port"],
                "online": info.get("online", False),
                "name": info.get("name", ""), "map": info.get("map", ""),
                "game": info.get("game", ""), "folder": info.get("folder", ""),
                "version": info.get("version", ""), "players": info.get("players", 0),
                "max_players": info.get("max_players", 0), "bots": info.get("bots", 0),
                "server_type": info.get("server_type", ""), "platform": info.get("platform", ""),
                "vac": info.get("vac", None), "players_on": info.get("players_on", ""),
                "err": info.get("err", ""),
            })

        data = {
            "servers": servers_data,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        # 注意：options 不用数字 scale（避免云端 T2I 返回 HTTP 422）。
        # 用 quality(full_page 保证整张图) + type jpeg 控制输出高画质。
        try:
            url = await self.html_render(
                LIST_TMPL, data,
                options={
                    "type": "jpeg",
                    "quality": self._render_quality(),
                    "full_page": True,
                },
            )
        except TypeError:
            # 兼容不支持 options 参数的旧版 AstrBot html_render
            url = await self.html_render(LIST_TMPL, data)
        return url

    # ==================== 列表文本 ====================
    def _list_text(self) -> str:
        if not self.servers:
            return "📭 暂无已保存的服务器。\n可用 /gmod-admin add <别名> <IP> [端口] 添加。"
        lines = [f"📋 已保存的服务器 ({len(self.servers)} 个):"]
        for alias, srv in self.servers.items():
            lines.append(f"  • [{alias}] {srv['ip']}:{srv['port']}")
        lines.append("\n在群里发送 [服务器列表] 可查看列表渲染图。")
        return "\n".join(lines)

    # ==================== 帮助文本 ====================
    def _help_text(self) -> str:
        listen = "✅ 已开启" if self._listen_enabled() else "❌ 已关闭"
        render = "✅ 已开启" if self._render_enabled() else "❌ 已关闭"
        return (
            "🎮 GMod 服务器查询插件 v1.0\n"
            "──────────────────────────\n"
            "所有成员可用:\n"
            "  /gmod <IP> [端口]   直接查询\n"
            "  /gmod <别名>        查询已保存的服务器\n"
            "  /gmod list          查看服务器列表（渲染图）\n"
            "  群内发送 <别名>      直接发别名自动查询（消息监听）\n"
            "  群内发送 [服务器列表]  自动生成列表渲染图\n"
            f"  （消息监听: {listen}｜列表渲染: {render}）\n"
            "\n"
            "管理(管理员):\n"
            "  /gmod-admin add <别名> <IP> [端口]  添加\n"
            "  /gmod-admin remove <别名>            删除\n"
            "  /gmod-admin list                    列表现存服务器\n"
            "\n"
            f"默认端口: {self._default_port()} | /gmod help 查看本帮助"
        )

    # ==================== 消息监听器 ====================
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_listen_alias(self, event: AstrMessageEvent):
        """监听所有消息：命中已保存别名则返回服务器信息；命中列表关键词则生成渲染图。"""
        if not self._listen_enabled():
            return

        message_str = event.message_str.strip()
        if not message_str or message_str.startswith("/"):
            return  # 空消息或注册指令，跳过避免与指令重复响应

        if self._listen_group_only():
            if not bool(getattr(event.message_obj, "group_id", None)):
                return

        # 1) 列表渲染关键词
        if self._render_enabled() and message_str in self._render_keywords():
            try:
                url = await self._render_list_image()
                yield event.image_result(url)
            except Exception as e:
                logger.error(f"服务器列表渲染失败: {e}")
                yield event.plain_result(self._list_text())
            return

        # 2) 匹配服务器别名
        hit = None
        if self._exact_match():
            if message_str in self.servers:
                hit = message_str
        else:
            for alias in self.servers:
                if alias in message_str:
                    hit = alias
                    break

        if hit is None:
            return  # 静默忽略

        srv = self.servers[hit]
        result = await self._query_server(hit, srv["ip"], srv["port"])
        yield event.plain_result(result)

    # ==================== 主指令 /gmod ====================
    @filter.command("gmod", alias={"GMOD", "服务器"})
    async def gmod(self, event: AstrMessageEvent):
        """GMod 服务器查询。用法: /gmod <别名 或 IP> [端口]，/gmod list 查看列表，/gmod help 查看帮助"""
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result(self._help_text())
            return

        param = parts[1].lower()

        if param in ("help", "?", "帮助"):
            yield event.plain_result(self._help_text())
            return

        if param in ("list", "servers", "列表", "服务器列表"):
            if self._render_enabled():
                try:
                    url = await self._render_list_image()
                    yield event.image_result(url)
                except Exception as e:
                    logger.error(f"服务器列表渲染失败: {e}")
                    yield event.plain_result(self._list_text())
            else:
                yield event.plain_result(self._list_text())
            return

        # 保留原始大小写用于别名匹配（别名大小写敏感）
        raw_param = parts[1]
        if raw_param in self.servers:
            srv = self.servers[raw_param]
            result = await self._query_server(raw_param, srv["ip"], srv["port"])
            yield event.plain_result(result)
            return

        if not self._looks_like_address(raw_param):
            yield event.plain_result(
                f"❌ 未找到别名 [{raw_param}]。\n"
                f"可用 /gmod list 查看已保存别名，/gmod help 查看帮助。"
            )
            return

        ip = raw_param
        port = int(parts[2]) if len(parts) > 2 else self._default_port()
        result = await self._query_server(None, ip, port)
        yield event.plain_result(result)

    # ==================== 管理指令组 /gmod-admin ====================
    @filter.command_group("gmod-admin")
    def gmod_admin(self):
        """GMod 服务器管理"""

    @gmod_admin.command("add")
    async def add(self, event: AstrMessageEvent, 别名: str, ip: str, port: int = None):
        """添加服务器: /gmod-admin add <别名> <IP> [端口]"""
        if not event.is_admin():
            yield event.plain_result("❌ 仅管理员可用。")
            return
        if port is None:
            port = self._default_port()
        if 别名 in self.servers:
            yield event.plain_result(f"❌ 别名 [{别名}] 已存在，可用 /gmod-admin remove {别名} 删除后重新添加。")
            return
        self.servers[别名] = {"ip": ip, "port": port}
        self._save()
        logger.info(f"已添加服务器: {别名} ({ip}:{port})")
        yield event.plain_result(
            f"✅ 已添加服务器:\n别名: {别名}\n地址: {ip}:{port}\n"
            f"现在你可以直接在群里发送 [{别名}] 查询它，或在群里发送 [服务器列表] 查看列表渲染图。"
        )

    @gmod_admin.command("remove", alias={"del", "删除"})
    async def remove(self, event: AstrMessageEvent, 别名: str):
        """删除服务器: /gmod-admin remove <别名>"""
        if not event.is_admin():
            yield event.plain_result("❌ 仅管理员可用。")
            return
        if 别名 in self.servers:
            del self.servers[别名]
            self._save()
            yield event.plain_result(f"✅ 已删除别名: {别名}")
        else:
            yield event.plain_result(f"❌ 未找到别名: {别名}，可用 /gmod-admin list 查看所有已保存的服务器。")

    @gmod_admin.command("list", alias={"列表"})
    async def admin_list(self, event: AstrMessageEvent):
        """列出已保存的服务器（管理组内）"""
        if not event.is_admin():
            yield event.plain_result("❌ 仅管理员可用。")
            return
        yield event.plain_result(self._list_text())

    # ==================== 生命周期 ====================
    async def terminate(self):
        """插件卸载时调用"""
        pass
