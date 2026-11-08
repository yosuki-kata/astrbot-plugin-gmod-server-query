# -*- coding: utf-8 -*-
"""GMod 服务器查询插件（重制版 v1.1.0）

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
    NAME = "gmod_a2s_server_query"   # 与 metadata.yaml 的 name 一致
    DEFAULT_PORT = 27015        # default_port
    QUERY_TIMEOUT = 5           # query_timeout
    ENABLE_LISTEN = True        # enable_listen
    LISTEN_ONLY_GROUP = True    # listen_only_group
    LISTEN_EXACT_MATCH = True   # listen_exact_match
    RENDER_IMAGE = True         # render_image
    RENDER_KEYWORDS = ["服务器列表", "列表"]  # render_keywords
    RENDER_QUALITY = 92         # render_quality
    RENDER_WIDTH = 1080         # render_width（1080p）
    LOCAL_T2I = ""              # render_local_t2i
    PREFER_LOCAL_T2I = False    # prefer_local_t2i


# ==================== 渲染图 HTML 模板（Jinja2） ====================
# 说明：背景图使用本地图片（插件目录 assets/bg.jpg），由 _bg_style() 转 base64 内联，
#      不存在时回退到 CSS 渐变，避免依赖外链、也避免云端 T2I 拉取外链超时。

# ---------- 公共样式片段 ----------
_COMMON_CSS = """
 * { margin: 0; padding: 0; box-sizing: border-box; }
 /* 背景层：绝对定位铺满整张长图（不是视口）。
    旧方案用 fixed 附着，在 full_page 长截图里会以视口为基准，
    背景只覆盖首屏高度、长图中段露出空白 —— 这是本次修复的核心。 */
 html {
     position: relative;
     min-height: 100%;
     width: 100%;
     background-color: #cfe3f5;
 }
 body {
     position: relative;
     font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
     color: #1f2937;
     padding: 20px;
     min-height: 100vh;
     width: 100%;
     background-color: transparent;
     background-image: none;
 }
 /* 真正的背景图：覆盖整张长图的物理尺寸，cover 填充并居中裁切 */
 #bgfill {
     position: absolute;
     top: 0;
     left: 0;
     width: 100%;
     height: 100%;
     min-height: 100vh;
     background-size: cover;
     background-position: center center;
     background-repeat: no-repeat;
     background-color: #cfe3f5;
     z-index: 0;
     pointer-events: none;
 }
 .wrap { position: relative; z-index: 1; max-width: 940px; margin: 0 auto; }
.card {
    background: rgba(255,255,255,0.88);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 14px;
    box-shadow: 0 4px 18px rgba(30,60,110,0.10);
    overflow: hidden;
}
.card-title { font-size: 17px; font-weight: 700; color: #1e40af; margin-bottom: 12px; }
.card-title .sub { float: right; font-size: 12px; font-weight: 400; color: #6b7280; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 26px; }
.row { display: flex; font-size: 14px; line-height: 1.85; min-width: 0; }
.row .k { color: #4b5563; white-space: nowrap; flex: none; }
.row .k::after { content: ":"; margin-right: 2px; }
.row .v { margin-left: 6px; font-weight: 600; word-break: break-all; min-width: 0; }
.v-blue   { color: #2563eb; }
.v-green  { color: #16a34a; }
.v-purple { color: #9333ea; }
.v-orange { color: #ea580c; }
.v-red    { color: #dc2626; }
.v-gray   { color: #6b7280; }
.v-cyan   { color: #0891b2; }
.v-pink   { color: #db2777; }
.srv-head {
    display: flex; align-items: center; justify-content: space-between;
    font-size: 15px; font-weight: 700; color: #1d4ed8;
    padding-bottom: 8px; margin-bottom: 10px;
    border-bottom: 1px solid rgba(30,64,175,0.15);
}
.srv-head .badge {
    flex: none; font-size: 12px; font-weight: 600;
    background: #dbeafe; color: #1d4ed8; border-radius: 10px; padding: 1px 10px;
}
.srv-head .badge.full { background: #fee2e2; color: #b91c1c; }
.srv-head .badge.off  { background: #e5e7eb; color: #4b5563; }
/* 玩家网格 */
.pgrid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px 12px; }
.pitem {
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(30,64,175,0.10);
    border-radius: 8px;
    padding: 7px 10px;
    font-size: 13px;
    display: flex; align-items: baseline; justify-content: space-between;
    overflow: hidden;
}
.pitem .n { color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.pitem .t { color: #6b7280; font-size: 12px; margin-left: 8px; flex: none; }
.pitem .idx { color: #9ca3af; font-size: 12px; margin-right: 6px; flex: none; }
.empty { text-align: center; color: #6b7280; font-size: 14px; padding: 26px 0; }
.footer {
    display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
    color: #4b5563; font-size: 12px;
    background: rgba(255,255,255,0.72);
    border-radius: 10px; padding: 10px 16px;
    margin-bottom: 4px;
}
.footer .hint { text-align: left; line-height: 1.6; }
.footer .meta { text-align: right; white-space: nowrap; flex: none; line-height: 1.6; }
"""
# ---------- 单服务器详情模板 ----------
DETAIL_TMPL = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<style>""" + _COMMON_CSS + """
</style>
</head>
<body>
<div id="bgfill" style="{{ bg_style }}"></div>
<div class="wrap">


    <!-- 服务器信息卡 -->
    <div class="card">
        <div class="srv-head">
            [{{ s.alias }}]服务器实时状态
            <span class="badge {{ 'full' if s.players >= s.max_players and s.max_players else '' }}">
                在线 {{ s.players }}/{{ s.max_players }}
            </span>
        </div>
        {% if s.online %}
        <div class="grid2">
            <div class="row"><span class="k">服务器名称</span><span class="v v-blue">{{ s.name or '-' }}</span></div>
            <div class="row"><span class="k">密码</span><span class="v {{ 'v-red' if s.password else 'v-gray' }}">{{ '是' if s.password else '否' }}</span></div>
            <div class="row"><span class="k">地址</span><span class="v v-blue">{{ s.ip }}:{{ s.port }}</span></div>
            <div class="row"><span class="k">bot数量</span><span class="v v-gray">{{ s.bots }}</span></div>
            <div class="row"><span class="k">游戏</span><span class="v v-green">{{ s.game or '-' }}</span></div>
            <div class="row"><span class="k">VAC</span><span class="v {{ 'v-green' if s.vac else 'v-gray' }}">{{ '安全' if s.vac else '未启用' }}</span></div>
            <div class="row"><span class="k">地图</span><span class="v v-pink">{{ s.map or '-' }}</span></div>
            <div class="row"><span class="k">在线玩家</span><span class="v {{ 'v-red' if s.players >= s.max_players and s.max_players else 'v-orange' }}">{{ s.players }}/{{ s.max_players }}</span></div>
            <div class="row"><span class="k">归类</span><span class="v v-purple">{{ s.folder or '-' }}</span></div>
            <div class="row"><span class="k">版本</span><span class="v v-purple">{{ s.version or '-' }}</span></div>
            <div class="row"><span class="k">AppID</span><span class="v v-gray">{{ s.app_id or '-' }}</span></div>
            <div class="row"><span class="k">延迟</span><span class="v {{ s.ping_cls }}">{{ s.ping }} ms</span></div>
            <div class="row"><span class="k">系统</span><span class="v v-gray">{{ s.platform_name }}</span></div>
            <div class="row"><span class="k">服务器类型</span><span class="v v-gray">{{ s.type_name }}</span></div>
        </div>
        {% else %}
        <div class="empty">❌ 服务器离线（{{ s.err }}）</div>
        {% endif %}
    </div>

    <!-- 在线玩家卡 -->
    {% if s.online %}
    <div class="card">
        <div class="card-title">
            在线玩家 ({{ s.player_total }})
            <span class="sub">按在线时长降序排序</span>
        </div>
        {% if players %}
        <div class="pgrid">
            {% for p in players %}
            <div class="pitem">
                <span class="n"><span class="idx">{{ p.idx }}.</span>{{ p.name }}</span>
                <span class="t">{{ p.duration }}</span>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty">暂无玩家在线 / 服务器未提供玩家列表</div>
        {% endif %}
    </div>
    {% endif %}

    <div class="footer">
        <div class="hint">
            提示: 发送 /gmod help 查看指令帮助<br>
            网络请求总耗时: {{ s.query_cost }}s
        </div>
        <div class="meta">生成于 {{ time }}</div>
    </div>
</div>
</body>
</html>
"""

# ---------- 多服务器总览模板 ----------
LIST_TMPL = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<style>""" + _COMMON_CSS + """
</style>
</head>
<body>
<div id="bgfill" style="{{ bg_style }}"></div>
<div class="wrap">

    {% if servers %}
        {% for s in servers %}
        <div class="card">
            <div class="srv-head">
                [{{ s.alias }}]服务器实时状态
                {% if not s.online %}
                    <span class="badge off">离线</span>
                {% else %}
                    <span class="badge {{ 'full' if s.players >= s.max_players and s.max_players else '' }}">
                        在线 {{ s.players }}/{{ s.max_players }}
                    </span>
                {% endif %}
            </div>
            {% if s.online %}
            <div class="grid2">
                <div class="row"><span class="k">服务器名称</span><span class="v v-blue">{{ s.name or '-' }}</span></div>
                <div class="row"><span class="k">密码</span><span class="v {{ 'v-red' if s.password else 'v-gray' }}">{{ '是' if s.password else '否' }}</span></div>
                <div class="row"><span class="k">地址</span><span class="v v-blue">{{ s.ip }}:{{ s.port }}</span></div>
                <div class="row"><span class="k">bot数量</span><span class="v v-gray">{{ s.bots }}</span></div>
                <div class="row"><span class="k">游戏</span><span class="v v-green">{{ s.game or '-' }}</span></div>
                <div class="row"><span class="k">VAC</span><span class="v {{ 'v-green' if s.vac else 'v-gray' }}">{{ '安全' if s.vac else '未启用' }}</span></div>
                <div class="row"><span class="k">地图</span><span class="v v-pink">{{ s.map or '-' }}</span></div>
                <div class="row"><span class="k">在线玩家</span><span class="v {{ 'v-red' if s.players >= s.max_players and s.max_players else 'v-orange' }}">{{ s.players }}/{{ s.max_players }}</span></div>
                <div class="row"><span class="k">归类</span><span class="v v-purple">{{ s.folder or '-' }}</span></div>
                <div class="row"><span class="k">版本</span><span class="v v-purple">{{ s.version or '-' }}</span></div>
                <div class="row"><span class="k">AppID</span><span class="v v-gray">{{ s.app_id or '-' }}</span></div>
                <div class="row"><span class="k">延迟</span><span class="v {{ s.ping_cls }}">{{ s.ping }} ms</span></div>
                <div class="row"><span class="k">系统</span><span class="v v-gray">{{ s.platform_name }}</span></div>
                <div class="row"><span class="k">服务器类型</span><span class="v v-gray">{{ s.type_name }}</span></div>
            </div>
            {% else %}
            <div class="empty">❌ 服务器离线（{{ s.err }}）</div>
            {% endif %}
        </div>
        {% endfor %}
    {% else %}
        <div class="card">
            <div class="empty">📭 暂无已保存的服务器<br>
                <span style="font-size:13px">使用 /gmod-admin add &lt;别名&gt; &lt;IP&gt; [端口] 添加</span>
            </div>
        </div>
    {% endif %}

    <div class="footer">
        <div class="hint">
            提示: 发送 /gmod help 查看指令帮助<br>
            共 {{ servers|length }} 台服务器 · 网络请求总耗时: {{ cost }}s
        </div>
        <div class="meta">生成于 {{ time }}</div>
    </div>
</div>
</body>
</html>
"""



class GModServerQuery(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.servers = {}  # 别名 -> {"ip": str, "port": int}
        self.data_file = self._resolve_data_file()
        self._migrate_legacy_data()
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

    def _render_detail_enabled(self) -> bool:
        """单服详情图开关，需同时开启 render_image。"""
        if not self._render_enabled():
            return False
        return bool(self._cfg("render_detail", True))

    def _render_quality(self) -> int:
        try:
            return max(40, min(100, int(self._cfg("render_quality", Config.RENDER_QUALITY))))
        except (TypeError, ValueError):
            return Config.RENDER_QUALITY

    def _render_width(self) -> int:
        """渲染图宽度（像素），默认 1080（1080p）。"""
        try:
            w = int(self._cfg("render_width", Config.RENDER_WIDTH))
        except (TypeError, ValueError):
            return Config.RENDER_WIDTH
        return max(480, min(2560, w))

    def _local_t2i(self) -> str:
        """本地 T2I 服务地址，未配置则返回空串。"""
        v = self._cfg("render_local_t2i", "")
        return v.strip() if isinstance(v, str) else ""

    def _prefer_local_t2i(self) -> bool:
        """是否优先走本地 T2I（需已配置地址）。"""
        if not self._local_t2i():
            return False
        return bool(self._cfg("prefer_local_t2i", False))

    # ==================== 数据持久化 ====================
    def _resolve_data_file(self) -> str:
        """确定 servers.json 的存放路径。

        规范要求持久化数据保存在 AstrBot 的 data/plugin_data/<插件名> 下，
        而不是插件源码目录（否则重装、升级会丢数据，也不利于迁移与审计）。
        优先用官方 StarTools.get_data_dir()，失败时按目录结构自行推导兜底。
        """
        plugin_name = Config.NAME
        # 1) 官方 API（AstrBot 4.x 提供）
        try:
            from astrbot.core.star.star_tools import StarTools
            d = StarTools.get_data_dir(plugin_name)
            if d:
                return str(os.path.join(str(d), "servers.json"))
        except Exception as e:
            logger.debug(f"[gmod] StarTools.get_data_dir 不可用，改用路径推导: {e}")

        # 2) 自行推导 data/plugin_data/<name>
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_root = self._find_data_root(base_dir) or base_dir
        for sub in ("plugin_data", "plugins_data"):
            d = os.path.join(data_root, sub, plugin_name)
            try:
                os.makedirs(d, exist_ok=True)
                return os.path.join(d, "servers.json")
            except Exception:
                continue

        # 3) 最后兜底：插件目录（与旧版行为一致，至少不丢功能）
        logger.warning("[gmod] 无法创建 plugin_data 目录，servers.json 将保存在插件目录")
        return os.path.join(base_dir, "servers.json")

    def _migrate_legacy_data(self):
        """把旧版本留在插件目录的 servers.json 迁移到新位置。"""
        legacy = os.path.join(os.path.dirname(os.path.abspath(__file__)), "servers.json")
        if os.path.abspath(legacy) == os.path.abspath(self.data_file):
            return
        if not os.path.isfile(legacy) or os.path.exists(self.data_file):
            return
        try:
            import shutil
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            shutil.copy2(legacy, self.data_file)
            logger.info(f"[gmod] 已将 servers.json 迁移到: {self.data_file}")
        except Exception as e:
            logger.warning(f"[gmod] servers.json 迁移失败: {e}")

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
    @staticmethod
    def _fmt_duration(seconds) -> str:
        """把秒数格式化为 HH:MM:SS。拿不到有效值时返回 --:--。"""
        try:
            sec = int(seconds)
        except (TypeError, ValueError):
            return "--:--"
        if sec < 0:
            return "--:--"
        h, rem = divmod(sec, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    @staticmethod
    def _platform_name(platform: str) -> str:
        p = (platform or "").lower()
        if p in ("l", "linux"):
            return "Linux"
        if p in ("w", "windows"):
            return "Windows"
        if p in ("m", "mac"):
            return "macOS"
        return "未知"

    @staticmethod
    def _type_name(server_type: str) -> str:
        t = (server_type or "").lower()
        if t in ("d", "dedicated"):
            return "专用"
        if t in ("l", "listen"):
            return "监听"
        if t in ("p", "proxymt"):
            return "代理"
        return "未知"

    @staticmethod
    def _ping_cls(ping: int) -> str:
        """按延迟分色：<50 绿，<100 橙，其余红。"""
        if ping is None:
            return "v-gray"
        if ping < 50:
            return "v-green"
        if ping < 100:
            return "v-orange"
        return "v-red"

    async def _query_one(self, alias, ip: str, port: int) -> dict:
        """查询单台服务器信息（a2s.info + a2s.players），返回字典。
        失败时带 online=False 与 err 说明，不影响其他服务器查询。
        """
        import time as _time

        base = {"alias": alias, "ip": ip, "port": port}
        started = _time.monotonic()
        try:
            loop = asyncio.get_running_loop()
            info = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: a2s.info((ip, port))),
                timeout=self._timeout(),
            )
            # 延迟取 info 查询耗时（毫秒），作为服务器响应延迟的近似值
            ping = int((_time.monotonic() - started) * 1000)

            # 玩家列表是附属信息，失败不影响主信息
            players_on = ""
            player_list = []
            try:
                ps = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: a2s.players((ip, port))),
                    timeout=self._timeout(),
                )
                if ps:
                    entries = []
                    for p in ps:
                        pname = (getattr(p, "name", "") or "").strip() or "未知玩家"
                        pdur = getattr(p, "duration", None)
                        entries.append({"name": pname, "duration": pdur})
                    # 按在线时长降序；无有效时长的排最后
                    entries.sort(
                        key=lambda x: (x["duration"] is None, -(x["duration"] or 0))
                        if isinstance(x["duration"], (int, float)) else (True, 0)
                    )
                    for i, e in enumerate(entries, 1):
                        player_list.append({
                            "idx": i,
                            "name": e["name"],
                            "duration": self._fmt_duration(e["duration"]),
                        })
                    shown = [e["name"] for e in entries[:8]]
                    if len(entries) > 8:
                        players_on = "、".join(shown) + f" 等{len(entries)}人"
                    else:
                        players_on = "、".join(shown)
            except Exception:
                players_on = ""
                player_list = []

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
                "password": bool(getattr(info, "password_protected", False)),
                "app_id": getattr(info, "app_id", None),
                "ping": ping,
                "players_on": players_on,
                "player_list": player_list,
                "player_total": len(player_list),
                "query_cost": f"{( _time.monotonic() - started):.2f}",
            })
        except asyncio.TimeoutError:
            base.update({"online": False, "err": "查询超时", "player_list": [], "player_total": 0})
        except Exception as e:
            base.update({"online": False, "err": str(e)[:40], "player_list": [], "player_total": 0})
        return base

    # ==================== 渲染图公共 ====================
    # AstrBot v4.13.0+ 的 file 类型配置，配置项里保存的是相对插件根目录的路径，
    # 形如 "files/render_background/xxx.jpg"。不同版本上传落盘位置可能不同
    # （data/plugins/<name>/files/... 或 data/plugins_data/<name>/files/... 等），
    # 因此这里以 AstrBot 的 data 根为搜索范围，逐层尝试。
    # 参考 astrbot/dashboard/services/config_service.py::upload_config_file
    _BG_FOLDER = "render_background"   # 本插件背景图配置键

    @staticmethod
    def _find_data_root(base_dir: str) -> str:
        """从插件目录向上回溯，定位 AstrBot 的 data 根目录。

        data/plugins/<name>/main.py  ->  data
        data/plugins_data/<name>/...  ->  data
        """
        cur = os.path.abspath(base_dir)
        for _ in range(6):
            parent = os.path.dirname(cur)
            if parent == cur or parent in ("/", "/root", "/home", "/srv", "/opt"):
                break
            cur = parent
            # 认定 parent 目录名为 data 时返回它
            if os.path.basename(cur) == "data":
                return cur
        # 兜底猜测：插件目录的祖先两级（data/plugins/<name> 的第 2 层上级）
        guess = os.path.abspath(os.path.join(base_dir, "..", ".."))
        return guess

    def _bg_search_roots(self) -> list:
        """返回所有可能存放 file 类型上传文件的根目录（按优先级）。

        AstrBot 不同版本上传落盘位置不同，已实测 v4.29.4 为：
            <data>/plugin_data/<插件名>/files/<配置键>/<文件名>
        因此这里既列出已知候选，也主动扫描 data 下所有包含同名插件目录的位置。
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        plugin_name = os.path.basename(base_dir)
        data_root = self._find_data_root(base_dir)

        # 1) 已实测/已知的候选（第一项即 v4.29.4 的真实位置）
        roots = [
            os.path.join(data_root, "plugin_data", plugin_name),   # 实测 v4.29.4
            base_dir,                                              # 插件源码根
            os.path.join(base_dir, "files"),
            os.path.join(base_dir, "files", self._BG_FOLDER),
            os.path.join(base_dir, "assets"),
            os.path.join(data_root, "plugins", plugin_name),        # 旧版
            os.path.join(data_root, "plugins_data", plugin_name),   # 备选拼写
        ]

        # 2) 主动扫描：data 下任一子目录中若存在同名插件目录，一并纳入
        try:
            if os.path.isdir(data_root):
                for entry in sorted(os.listdir(data_root)):
                    cand = os.path.join(data_root, entry, plugin_name)
                    if os.path.isdir(cand):
                        roots.append(cand)
        except Exception as e:
            logger.warning(f"[gmod] 扫描 data 目录失败: {e}")

        roots.extend([
            os.path.join(data_root, "files"),
            os.path.join(data_root, "files", plugin_name),
            data_root,
            os.getcwd(),
        ])

        # 去重并保持顺序
        seen = set()
        out = []
        for r in roots:
            r = os.path.abspath(r)
            if r not in seen:
                seen.add(r)
                out.append(r)
        return out

    def _resolve_all_bg_paths(self, val) -> list:
        """把配置值里**所有能定位到的**背景图路径全部收集出来（不随机、不截断）。

        用于多图场景下的随机抽取：只有先拿到完整候选集，随机才有意义。
        """
        if not val:
            return []
        out = []
        if isinstance(val, (list, tuple)):
            for item in val:
                for p in self._resolve_all_bg_paths(item):
                    if p not in out:
                        out.append(p)
            return out
        p = self._resolve_bg_path(val)
        return [p] if p else []

    def _resolve_bg_path(self, val) -> str:
        """从配置值中解析出背景图实际文件路径。

        支持的结构：
          - str  "/a/b.jpg" 或 "files/render_background/bg.png"
          - list ["files/render_background/bg.png", ...]  → 随机抽取一张
          - dict {"path": ...} / {"file": ...} / {"name": ...} 等
        """
        if not val:
            return ""
        candidates = []
        if isinstance(val, str):
            candidates.append(val)
        elif isinstance(val, (list, tuple)):
            # 多图：先收集全部可用路径，再随机抽一张（单张时等于原行为）
            import random

            found = self._resolve_all_bg_paths(val)
            if not found:
                return ""
            if len(found) == 1:
                logger.info(f"[gmod] 背景图命中: {found[0]}")
                return found[0]
            picked = random.choice(found)
            logger.info(f"[gmod] 背景图随机命中（{len(found)} 张可选）: {picked}")
            return picked
        elif isinstance(val, dict):
            for key in ("path", "file", "file_path", "abs_path", "url",
                        "name", "filename", "id", "uuid"):
                if val.get(key):
                    candidates.append(str(val[key]))
        else:
            return ""

        roots = self._bg_search_roots()
        checked = []
        for c in candidates:
            c = (c or "").strip()
            if not c:
                continue
            # 1) 绝对路径直接判定
            if os.path.isabs(c) and os.path.isfile(c):
                logger.info(f"[gmod] 背景图命中（绝对路径）: {c}")
                return c
            # 2) 相对路径在所有候选根下逐一尝试
            for d in roots:
                try:
                    p = os.path.normpath(os.path.join(d, c))
                except Exception:
                    continue
                checked.append(p)
                if os.path.isfile(p):
                    logger.info(f"[gmod] 背景图命中: {p}")
                    return p

        # 3) 兜底：在候选根下的 files/<BG_FOLDER>/ 目录里找第一张图
        for d in roots:
            for probe in (os.path.join(d, "files", self._BG_FOLDER),
                          os.path.join(d, self._BG_FOLDER)):
                if not os.path.isdir(probe):
                    continue
                try:
                    for fn in sorted(os.listdir(probe)):
                        if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                            p = os.path.join(probe, fn)
                            logger.info(f"[gmod] 背景图命中（目录兜底）: {p}")
                            return p
                except Exception as e:
                    logger.warning(f"[gmod] 读取目录失败 {probe}: {e}")

        # 4) 最后兜底：在 data 根内按文件名限深反查
        found = self._search_uploaded_file(candidates)
        if found:
            return found

        logger.warning(
            f"[gmod] 背景图未能定位。原始值: {val!r}\n"
            f"  已尝试根目录: {roots}\n"
            f"  已尝试路径(前6条): {checked[:6]}\n"
            f"  提示: 可在服务器执行 find <data根> -name '<文件名>' 确认实际位置"
        )
        return ""

    def _search_uploaded_file(self, candidates) -> str:
        """在 AstrBot 数据目录附近有限深度递归查找上传的文件。
        file 类型配置常只保存文件名或 UUID，需要反查真实路径。
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 优先从插件根开始（file 类型上传落在 <插件根>/files/...），
        # 再补上 AstrBot 的 data 根（不同版本落盘位置有差异）
        roots = [base_dir]
        data_root = self._find_data_root(base_dir)
        if os.path.isdir(data_root):
            roots.append(data_root)
        cur = base_dir
        for _ in range(3):
            parent = os.path.dirname(cur)
            if parent == cur or parent in ("/", "/storage", "/storage/emulated",
                                          "/storage/emulated/0", "/sdcard"):
                break
            if parent not in roots:
                roots.append(parent)
            cur = parent

        names = set()
        for c in candidates:
            c = (c or "").strip().strip("/\\")
            if not c:
                continue
            names.add(os.path.basename(c))
            names.add(c)
        if not names:
            return ""

        # 反查只认图片扩展名，避免匹配到同名无关文件
        img_exts = (".jpg", ".jpeg", ".png", ".webp")

        for root in roots:
            for dirpath, dirnames, filenames in os.walk(root):
                depth = dirpath[len(root):].count(os.sep)
                if depth >= 4:
                    dirnames[:] = []
                    continue
                # 跳过无关/超大目录，减少遍历成本
                dirnames[:] = [
                    d for d in dirnames
                    if d not in (".git", "__pycache__", "node_modules",
                                 "site-packages", ".venv", "venv", "dist-info")
                ]
                for fn in filenames:
                    if fn in names and fn.lower().endswith(img_exts):
                        p = os.path.join(dirpath, fn)
                        if os.path.isfile(p):
                            logger.info(f"[gmod] 背景图已定位: {p}")
                            return p
        return ""

    def _load_bg_b64(self, path: str) -> str:
        """读取背景图并转 base64，带进程内缓存。

        缓存键 = 绝对路径 + mtime + size，所以同名文件被替换后会自动失效重读，
        不会出现「换了图但渲染还是旧背景」的问题。
        多张大图（1080p 背景常见 1-3 MB）每次渲染都重读+base64 很吃内存和时间，
        缓存后只有首次读取有成本。
        """
        import base64

        try:
            st = os.stat(path)
            key = (os.path.abspath(path), int(st.st_mtime), int(st.st_size), st.st_ino)
        except Exception:
            # stat 失败（文件消失/权限问题）直接放弃缓存，走原路径
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("ascii")

        cache = self.__dict__.setdefault("_bg_b64_cache", {})
        hit = cache.get(key)
        if hit is not None:
            logger.debug(f"[gmod] 背景图命中缓存: {path}")
            return hit

        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")

        # 只保留少量条目，避免长时间运行后累积内存
        if len(cache) >= 8:
            cache.clear()
        cache[key] = b64
        logger.debug(f"[gmod] 背景图已加载并缓存: {path} ({st.st_size} bytes)")
        return b64

    def _assets_bg_candidates(self, base_dir: str) -> list:
        """返回 assets 目录下所有可用的背景图候选，供随机抽取。

        优先取约定的 bg.jpg / bg.jpeg / bg.png / bg.webp；
        同时扫描目录下任意其他图片文件（如 1.jpg、2.png），
        方便用户直接丢多张图进去做轮换，不必改名。
        """
        img_exts = (".jpg", ".jpeg", ".png", ".webp")
        assets = os.path.join(base_dir, "assets")
        if not os.path.isdir(assets):
            return []

        cands = []
        # 1) 约定的固定文件名（优先，保持向后兼容）
        for name in ("bg.jpg", "bg.jpeg", "bg.png", "bg.webp"):
            p = os.path.join(assets, name)
            if os.path.isfile(p):
                cands.append(p)

        # 2) 目录内其他图片文件，按文件名排序保证结果可预期
        try:
            for fn in sorted(os.listdir(assets)):
                if not fn.lower().endswith(img_exts):
                    continue
                p = os.path.join(assets, fn)
                if os.path.isfile(p) and p not in cands:
                    cands.append(p)
        except Exception as e:
            logger.warning(f"[gmod] 扫描 assets 目录失败: {e}")

        return cands

    def _bg_style(self) -> str:
        """生成背景样式。严格优先级：
           1) 插件配置项 render_background（WebUI 上传，多张时随机抽取）
           2) 插件目录 assets/bg.jpg|jpeg|png|webp（多张时也随机）
           3) 柔和渐变兜底

        关键点：配置项里的图**全部定位不到**时，要回退到 assets，
        而不是直接掉到渐变。这样用户误删上传文件后仍能看到默认背景图。
        图片统一转 base64 内联，避免云端 T2I 拉取外链超时；读取结果带缓存。
        """
        import random

        base_dir = os.path.dirname(os.path.abspath(__file__))

        # ---------- 优先级 1：配置项 ----------
        raw_cfg = self._cfg("render_background", [])
        path = self._resolve_bg_path(raw_cfg)
        source = "配置项"

        # ---------- 优先级 2：assets 目录 ----------
        if not path:
            cands = self._assets_bg_candidates(base_dir)
            if cands:
                path = random.choice(cands)
                source = "assets"
                if len(cands) > 1:
                    logger.info(f"[gmod] assets 背景随机命中（{len(cands)} 张可选）: {path}")
                else:
                    logger.info(f"[gmod] assets 背景命中: {path}")
            elif raw_cfg:
                # 配置了但找不到，assets 也没有 —— 这种情况值得告警
                logger.warning(f"[gmod] 背景图回退为默认渐变。配置原始值: {raw_cfg!r}")

        # ---------- 优先级 3：渐变 ----------
        if path:
            try:
                ext = path.rsplit(".", 1)[-1].lower()
                if ext not in ("jpg", "jpeg", "png", "webp"):
                    raise ValueError(f"不支持的图片格式: {ext}")
                mime = "jpeg" if ext in ("jpg", "jpeg") else ("png" if ext == "png" else "webp")
                b64 = self._load_bg_b64(path)
                logger.debug(f"[gmod] 使用背景图（来源: {source}）: {path}")
                # 只输出图片本身；铺满/居中/裁切由 CSS 中的 #bgfill 统一控制
                return f"background-image:url('data:image/{mime};base64,{b64}');"
            except Exception as e:
                logger.warning(f"加载背景图失败({path}): {e}")

        return (
            "background-image:linear-gradient(160deg,#e8f2fc 0%,#cfe3f5 45%,#bcd6ee 100%);"
        )

    def _render_options(self) -> dict:
        """渲染选项。full_page 保证长图完整不裁切。"""
        return {
            "type": "jpeg",
            "quality": self._render_quality(),
            "full_page": True,
            "width": self._render_width(),
        }

    async def _render_via_custom_endpoint(self, tmpl: str, data: dict, endpoint: str) -> str:
        """直接调用指定的 text2img 端点渲染（用于本地 T2I / 自定义端点）。

        与 AstrBot NetworkRenderStrategy 的协议保持一致：
            POST {endpoint}/generate  {"tmpl":..., "tmpldata":..., "json":True, "options":...}
        返回图片 URL；失败抛异常。
        """
        import aiohttp

        url = endpoint.removesuffix("/")
        if not url.endswith("text2img"):
            url += "/text2img"
        payload = {
            "tmpl": tmpl,
            "tmpldata": data,
            "json": True,
            "options": self._render_options(),
        }
        timeout = aiohttp.ClientTimeout(total=max(15, self._timeout() * 4))
        # trust_env=False：不读取环境变量中的代理配置，避免请求被意外劫持到未知代理
        async with aiohttp.ClientSession(timeout=timeout, trust_env=False) as session:
            async with session.post(f"{url}/generate", json=payload) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                ret = await resp.json()
                img_id = (ret.get("data") or {}).get("id")
                if not img_id:
                    raise RuntimeError(f"响应缺少 data.id: {str(ret)[:120]}")
                return f"{url}/{img_id}"

    async def _render_html(self, tmpl: str, data: dict) -> str:
        """统一渲染入口，渲染优先级（可配置）：

            prefer_local_t2i = false（默认）: 外部 T2I → 本地 T2I → 抛异常（由调用方回退文字）
            prefer_local_t2i = true          : 本地 T2I → 外部 T2I → 抛异常

        未配置本地 T2I 地址时，本地环节自动跳过。
        """
        local = self._local_t2i()
        errors = []

        async def _try_local():
            if not local:
                return None
            try:
                url = await self._render_via_custom_endpoint(tmpl, data, local)
                logger.info(f"[gmod] 已用本地 T2I 渲染: {local}")
                return url
            except Exception as e:
                errors.append(f"本地T2I({local}): {e}")
                logger.warning(f"[gmod] 本地 T2I 渲染失败: {e}")
                return None

        async def _try_remote():
            try:
                url = await self.html_render(tmpl, data, options=self._render_options())
                return url
            except TypeError:
                # 旧版 html_render 不支持 options
                try:
                    return await self.html_render(tmpl, data)
                except Exception as e:
                    errors.append(f"外部T2I: {e}")
                    return None
            except Exception as e:
                errors.append(f"外部T2I: {e}")
                logger.warning(f"[gmod] 外部 T2I 渲染失败: {e}")
                return None

        order = [_try_local, _try_remote] if self._prefer_local_t2i() else [_try_remote, _try_local]
        for fn in order:
            url = await fn()
            if url:
                return url

        raise RuntimeError("渲染失败（外部/本地 T2I 均不可用）: " + " | ".join(errors))

    # ==================== 单服务器详情渲染图 ====================
    async def _render_detail_image(self, alias, ip: str, port: int) -> str:
        """查询单台服务器并渲染为详情图，返回图片 URL。"""
        import datetime

        info = await self._query_one(alias, ip, port)
        info.update({
            "platform_name": self._platform_name(info.get("platform", "")),
            "type_name": self._type_name(info.get("server_type", "")),
            "ping_cls": self._ping_cls(info.get("ping")),
            "ping": info.get("ping") if info.get("ping") is not None else "--",
            "query_cost": info.get("query_cost", "0.00"),
        })
        data = {
            "s": info,
            "players": info.get("player_list", []),
            "bg_style": self._bg_style(),
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        return await self._render_html(DETAIL_TMPL, data)

    async def _reply_detail(self, event, alias, ip: str, port: int):
        """统一出口：渲染详情图；未开启渲染或渲染失败时回退为文字。
        返回要 yield 的结果对象。
        """
        if self._render_detail_enabled():
            try:
                url = await self._render_detail_image(alias, ip, port)
                return event.image_result(url)
            except Exception as e:
                logger.error(f"单服详情渲染失败，回退文字: {e}")
                text = await self._query_server(alias, ip, port)
                return event.plain_result(text + "\n" + self._render_fail_hint(e))
        text = await self._query_server(alias, ip, port)
        return event.plain_result(text)

    # ==================== 单服务器查询 & 格式化 ====================
    async def _query_server(self, alias, ip: str, port: int) -> str:
        """查询单台服务器并格式化为文本返回（渲染失败时的回退）。"""
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
            f"    地址: {info.get('ip')}:{info.get('port')}\n"
            f"    游戏: {info.get('game', '') or '-'}\n"
            f"    地图: {info.get('map', '') or '-'}\n"
            f"    当前在线: {info.get('players', 0)}/{info.get('max_players', 0)}\n"
            f"    延迟: {info.get('ping', '-')} ms"
        )
        players_on = info.get("players_on", "") or ""
        if players_on:
            text += f"\n    在线玩家: {players_on}"
        return text

    # ==================== 列表渲染图 ====================
    async def _query_all(self) -> list:
        """并发查询所有服务器，返回原始查询结果列表（不涉及渲染）。"""
        tasks = []
        for alias, srv in self.servers.items():
            tasks.append(self._query_one(alias, srv["ip"], srv["port"]))
        return await asyncio.gather(*tasks) if tasks else []

    async def _render_list_image(self) -> str:
        """并发查询所有服务器，将列表渲染为图片，返回图片 URL。"""
        results = await self._query_all()
        return await self._render_list_image_from(results)

    async def _render_list_image_from(self, results) -> str:
        """用已有的查询结果渲染总览图，避免重复查询。"""
        import datetime
        import time as _t

        _started = _t.monotonic()
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
                "password": info.get("password", False),
                "app_id": info.get("app_id", None),
                "ping": info.get("ping", "--"),
                "ping_cls": self._ping_cls(info.get("ping")),
                "platform_name": self._platform_name(info.get("platform", "")),
                "type_name": self._type_name(info.get("server_type", "")),
            })

        data = {
            "servers": servers_data,
            "bg_style": self._bg_style(),
            "cost": f"{(_t.monotonic() - _started):.2f}",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        return await self._render_html(LIST_TMPL, data)

    # ==================== 列表文本 ====================
    def _list_text(self) -> str:
        """仅列出已保存的别名/地址（管理视角，不含实时状态）。"""
        if not self.servers:
            return "📭 暂无已保存的服务器。\n可用 /gmod-admin add <别名> <IP> [端口] 添加。"
        lines = [f"📋 已保存的服务器 ({len(self.servers)} 个):"]
        for alias, srv in self.servers.items():
            lines.append(f"  • [{alias}] {srv['ip']}:{srv['port']}")
        lines.append("\n在群里发送 [服务器列表] 可查看列表渲染图。")
        return "\n".join(lines)

    @staticmethod
    def _is_t2i_error(err: Exception) -> bool:
        """判断异常是否来自 T2I（HTML 转图片）服务不可用。"""
        s = str(err).lower()
        keys = ("t2i", "endpoint", "text2img", "http 503", "http 502",
                "http 504", "cannot connect to host", "all endpoints failed",
                "timeout", "connection")
        return any(k in s for k in keys)

    def _servers_to_text(self, results) -> str:
        """把并发查询结果格式化为完整文本总览（渲染失败时的回退）。

        不依赖 T2I，输出与渲染图等价的服务器状态信息。
        """
        if not results:
            return self._list_text()

        lines = [f"📋 服务器状态总览（{len(results)} 台）", ""]
        for i, info in enumerate(results, 1):
            alias = info.get("alias") or info.get("ip", "")
            lines.append(f"【{i}】[{alias}] {info.get('ip')}:{info.get('port')}")
            if not info.get("online"):
                lines.append(f"  ❌ 离线（{info.get('err', '未知原因')}）")
                lines.append("")
                continue
            name = info.get("name") or "-"
            lines.append(f"  名称：{name}")
            lines.append(f"  地图：{info.get('map') or '-'}")
            lines.append(f"  玩家：{info.get('players', 0)}/{info.get('max_players', 0)}"
                         f"  | 延迟：{info.get('ping', '-')} ms"
                         f"  | 密码：{'是' if info.get('password') else '否'}")
            pv = info.get("players_on") or ""
            if pv:
                lines.append(f"  在线：{pv}")
            lines.append("")

        text = "\n".join(lines).rstrip()
        # 超长时截断，避免部分平台消息长度上限导致发送失败
        if len(text) > 1800:
            text = text[:1800] + "\n…（内容过长已截断）"
        return text

    def _render_fail_hint(self, err: Exception) -> str:
        """渲染失败时给用户的说明（区分 T2I 故障与其他问题）。"""
        if self._is_t2i_error(err):
            return "（图片渲染服务暂时不可用，已改用文字显示。可稍后再试，或在 AstrBot 中配置本地 t2i）"
        return "（图片渲染失败，已改用文字显示）"

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
                results = await self._query_all()
            except Exception as e:
                logger.error(f"服务器查询失败: {e}")
                yield event.plain_result(self._list_text())
                return
            try:
                url = await self._render_list_image_from(results)
                yield event.image_result(url)
            except Exception as e:
                # 渲染失败（常见于外部 T2I 服务不可用）→ 回退为完整文本总览
                logger.error(f"服务器列表渲染失败，回退文字: {e}")
                yield event.plain_result(
                    self._servers_to_text(results) + "\n" + self._render_fail_hint(e)
                )
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
        yield await self._reply_detail(event, hit, srv["ip"], srv["port"])

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
            yield await self._reply_detail(event, raw_param, srv["ip"], srv["port"])
            return

        if not self._looks_like_address(raw_param):
            yield event.plain_result(
                f"❌ 未找到别名 [{raw_param}]。\n"
                f"可用 /gmod list 查看已保存别名，/gmod help 查看帮助。"
            )
            return

        ip = raw_param
        port = int(parts[2]) if len(parts) > 2 else self._default_port()
        yield await self._reply_detail(event, None, ip, port)

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
