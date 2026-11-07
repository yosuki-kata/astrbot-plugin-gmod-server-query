# 🎮 gmod服务器查询插件：重制 · GMod Server Query Plugin

![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **一个面向 AstrBot 的 Garry's Mod (GMod) 服务器在线查询插件（重制版）。**
> >
> **An online server query plugin for Garry's Mod (GMod) running on AstrBot (remastered).**

基于原 v3.3.2 功能彻底重写，回归 **1.0** 作为全新起点——代码结构更清晰、命名更规范，并已规避历次版本踩过的所有坑。

Built from scratch by rewriting the old v3.3.2 — returning to **1.0** as a fresh start: cleaner code structure, more standardized naming, and all the pitfalls from previous releases have been avoided.

> ⚠️ **平台声明 / Platform statement**：本插件**仅确定在 aiocqhttp（OneBot v11 适配器）平台下能正常使用，其他平台是否可用未知**。请优先在 **aiocqhttp** 平台下部署使用。
>
> This plugin is **confirmed to work only on the aiocqhttp (OneBot v11 adapter) platform; behavior on other platforms is unknown.** Please deploy it on **aiocqhttp**.

---

## ✨ 功能一览 / Features

- **别名管理**：用 **/gmod-admin** 指令组，把 IP 与端口保存为易记别名。
  **Alias management**: Use the **/gmod-admin** command group to save IP / port as easy-to-remember aliases.
- **IP 或别名查询**：**/gmod &lt;别名或IP&gt;** 快速查询服务器在线信息（在线人数、地图、延迟等）。
  **IP or alias query**: **/gmod &lt;alias或IP&gt;** quickly queries server online info (players, map, latency, etc.).
- **超时控制**：所有网络查询套用可配置超时（默认 5 秒），避免卡住。
  **Timeout control**: All network queries apply a configurable timeout (default 5 s) to avoid hanging.
- **消息监听**：群内直接发送已保存别名，即自动查询（可开关、可限定仅群聊、可精确或包含匹配）。
  **Message listening**: Sending a saved alias in a group auto-queries it (toggleable, group-only, exact / contains match).
- **列表渲染图**：发送「服务器列表」或运行 **/gmod list** 时，生成高画质 JPEG 列表图片（画质与宽度均可配置，默认 1080p）。
  **List render image**: Sending "服务器列表" or running **/gmod list** generates a high-quality JPEG list image (quality and width configurable, 1080p by default).
- **单服详情图**：查询单台服务器时渲染为详情卡片，包含玩家名单与服务器参数。
  **Detail image**: Querying a single server renders a detail card with the player list and server properties.
- **背景图**：支持上传自定义背景图，铺满整张长图不失真，未配置时使用内置渐变。
  **Background**: Upload a custom background that fills the entire long image; falls back to a built-in gradient.
- **三级渲染兜底**：外部 T2I → 本地 T2I → 文字输出，任一渲染服务故障都能给出完整文字总览。
  **Three-level render fallback**: Remote T2I → Local T2I → Plain text, always delivering a complete text summary when renderers fail.
- **可视化配置**：通过 AstrBot 管理面板可视化配置全部选项。
  **Visual config**: All options are configurable from the AstrBot admin panel.

---

## 📦 安装 / Installation

### 方式一：插件市场安装（推荐） / Method 1: AstrBot Plugin Market (recommended)

发布后，直接在 AstrBot 管理面板「**插件市场**」搜索 **gmod**，安装即可，无需处理 zip。

Once published, install directly from the AstrBot admin panel: **Plugin Market → search gmod** and install. No zip handling needed.

### 方式二：手动 zip 安装 / Method 2: Manual zip install

> **压缩包命名规范 / Zip naming rule**：成品压缩包须命名为 **V主版本号.次版本号.修订版本号.zip**（如 **V1.0.2.zip**），并与 **metadata.yaml** 中的 **version** 字段严格一致。其他命名（如 **插件_v1.0.zip**）不推荐。
>
> The final package must be named **V&lt;major&gt;.&lt;minor&gt;.&lt;patch&gt;.zip** (e.g. **V1.0.2.zip**), strictly matching the **version** field in **metadata.yaml**. Other names (like **插件_v1.0.zip**) are NOT recommended.
>

1. 打包为 **V1.0.2.zip**，将 **main.py**、**metadata.yaml**、**_conf_schema.json**、**requirements.txt** 放在 zip 根目录（不要放进子文件夹）。
   Create the zip: **V1.0.2.zip**, with **main.py**, **metadata.yaml**, **_conf_schema.json**, **requirements.txt** at the zip root (not inside a sub-folder).
2. 在 AstrBot 管理面板「**插件管理 → 安装**」上传 zip。
   In the AstrBot admin panel: **Plugin Management → Install → upload the zip**.
3. 安装完成后，重启插件即可生效。
   Restart the plugin for it to take effect.

> **metadata.yaml** 必须使用官方字段（**name**、**display_name**、**version**、**author**、**repo**、**astrbot_version**、**tags** 等）。
> **metadata.yaml** must use the official fields (**name**, **display_name**, **version**, **author**, **repo**, **astrbot_version**, **tags**, ...).

### 方式三：git 仓库克隆安装（获取最新更新）/ Method 3: Clone from git repo (for the latest updates)

进入 AstrBot 插件目录，直接克隆本仓库即可随时拉取最新版本：

Change into AstrBot's plugin directory and clone this repo to always stay at the latest version:

```bash
cd astrbot/data/plugin
git clone https://github.com/yosuki-kata/astrbot-plugin-gmod-server-query.git
```

> 说明：**git clone 拉取到的即为仓库最新源码**，无需手动下载 zip。
> Note: **git clone fetches the latest source** directly from the repo — no manual zip download needed.

---

## 📖 使用说明 / Usage

### 对所有成员可用 / For all members

**/gmod &lt;IP&gt; [port]**　　　直接查询某服务器 &middot; Query a server directly
**/gmod &lt;alias&gt;**　　　　　查询已保存的服务器（别名区分大小写）&middot; Query a saved server (alias is case-sensitive)
**/gmod list**　　　　　　　　查看服务器列表（生成渲染图）&middot; Show server list (rendered image)
**/gmod help**　　　　　　　　查看帮助 &middot; Show help

群内发送 **&lt;alias&gt;**　　　　直接发别名，自动查询（消息监听，可配置）&middot; Send an alias in group → auto query
群内发送 **[服务器列表]**　　　自动生成列表渲染图 &middot; Auto-generate list render image

### 管理指令（管理员） / Admin commands (administrator)

> 管理功能使用独立的 **gmod-admin 指令组**（不是 **/gmod &lt;xxx&gt;** 子命令形式）。指令必须以 **/gmod-admin** 开头。
>
> Admin features use an **independent gmod-admin command group** (NOT a **/gmod &lt;xxx&gt;** subcommand). You must type the command starting with **/gmod-admin**.

**/gmod-admin add &lt;alias&gt; &lt;IP&gt; [port]**　　添加服务器 &middot; Add a server
**/gmod-admin remove &lt;alias&gt;**　　　　　　　删除服务器 &middot; Remove a server
**/gmod-admin list**　　　　　　　　　　　　　列出现存服务器 &middot; List saved servers

指令组与 **/gmod** 的对应关系 / Mapping between the command groups：

| 你想做的事 / What you want | 普通查询指令 / Normal command | 管理指令 / Admin command |
|-----------|------------|---------|
| 查询服务器 / Query server | **/gmod &lt;alias-or-IP&gt;** | — |
| 查看列表 / View list | **/gmod list** | **/gmod-admin list** |
| 添加服务器 / Add server | — | **/gmod-admin add &lt;alias&gt; &lt;IP&gt; [port]** |
| 删除服务器 / Remove server | — | **/gmod-admin remove &lt;alias&gt;** |

**示例 / Examples**：

**/gmod-admin add 我的服 192.168.1.100 27015**　　# 添加别名「我的服」/ Add alias「我的服」
**/gmod-admin remove 我的服**　　　　　　　　　　　# 删除别名「我的服」/ Remove alias「我的服」
**/gmod-admin list**　　　　　　　　　　　　　　　# 查看所有已保存服务器 / List all saved servers

---

## ⚙️ 配置项 / Configuration（可视化面板）

| Key | 默认值 / Default | 说明 / Description |
|----------|--------|------|
| **default_port** | 27015 | 默认查询端口 / Default query port |
| **query_timeout** | 5 | 查询超时时间（秒）/ Query timeout in seconds |
| **enable_listen** | true | 是否启用消息监听（发别名自动查询）/ Enable message listening (alias auto-query) |
| **listen_only_group** | true | 是否仅在群聊中监听 / Listen only in group chats |
| **listen_exact_match** | true | 仅精确匹配别名，或包含匹配别名 / Exact match or contains match for aliases |
| **render_image** | true | 是否用图片渲染服务器列表 / Render server list as image |
| **render_detail** | true | 是否用图片渲染单服务器详情 / Render single-server detail as image |
| **render_keywords** | ["服务器列表","列表"] | 触发列表渲染图的监听关键词 / Keywords that trigger list render image |
| **render_quality** | 92 | 渲染图 JPEG 画质（1-100，建议 80-95）/ JPEG quality (1-100, suggested 80-95) |
| **render_width** | 1080 | 渲染图输出宽度（px），默认 1080p，可填 1440 / 1920，范围 480-2560 / Render output width in px, default 1080p, 480-2560 |
| **render_background** | [] | 渲染图背景图，支持 jpg/jpeg/png/webp，留空则用插件目录 assets/bg.jpg，再没有则使用内置渐变 / Background image for rendering |
| **render_local_t2i** | "" | 本地 T2I 服务地址，如 http://127.0.0.1:8000，留空则不启用 / Local T2I service endpoint, leave empty to disable |
| **prefer_local_t2i** | false | 是否优先走本地 T2I（需先填 render_local_t2i）/ Prefer local T2I (requires render_local_t2i) |

### 渲染优先级 / Render Priority

插件按以下顺序尝试出图，任一成功即返回：

The plugin tries the following strategies in order and returns on the first success:

| 顺序 | 策略 / Strategy | 说明 / Description |
|------|------|------|
| 1 | 外部 T2I / Remote T2I | AstrBot 全局配置的 T2I 服务 / The global T2I service configured in AstrBot |
| 2 | 本地 T2I / Local T2I | 你在 **render_local_t2i** 填写的自建服务 / Your own endpoint in **render_local_t2i** |
| 3 | 文字输出 / Plain text | 前两者都失败时，输出完整文字总览（含在线玩家名单）/ Falls back to full text summary including player list |

勾选 **prefer_local_t2i** 后，顺序变为「本地 T2I → 外部 T2I → 文字输出」。

If **prefer_local_t2i** is enabled, the order becomes Local T2I → Remote T2I → Plain text.

> **关于本地 T2I / About Local T2I**
>
> AstrBot 内置的本地渲染策略不支持自定义 HTML 模板（调用会直接抛 NotImplementedError），因此本插件的「本地 T2I」需要你自建一个兼容端点。该端点需满足与官方一致的协议：
>
> AstrBot's built-in local strategy does not support custom HTML templates, so the local T2I here requires a self-hosted endpoint with the same protocol as the official one:
>
> 请求 / Request：**POST {endpoint}/generate**
>
> 请求体 / Body：**{"tmpl": 模板字符串, "tmpldata": 数据字典, "json": true, "options": {"type":"jpeg","quality":92,"full_page":true,"width":1080}}**
>
> 响应 / Response：**{"data": {"id": "xxx"}}**，插件据此拼接出图片地址 **{endpoint}/{id}** / The plugin builds the image URL as **{endpoint}/{id}**

---

## 🔧 技术要点 / Technical Notes

- 列表渲染图**不传数字 scale**，用 **quality + full_page + width** 控制清晰度（规避云端 T2I 的 HTTP 422）。
  The list render image does **NOT** pass a numeric **scale**; it uses **quality + full_page + width** for sharpness (avoids cloud T2I HTTP 422).
- **html_render** 对旧版无 **options** 参数的版本，做了 **TypeError 兼容回退**。
  **html_render** has a **TypeError fallback** for older versions without the **options** parameter.
- 渲染链为「外部 T2I → 本地 T2I → 文字」三级兜底，两路渲染均失败时输出**完整文字总览**（服务器信息 + 在线玩家名单），不会退化为仅有别名清单。
  The render chain has three levels of fallback; when both render paths fail, a **full text summary** (server info + player list) is output instead of a bare alias list.
- 背景图使用**独立背景层**铺满整张长图，而非附着在 html/body 上。若直接给 html/body 用 fixed 附着，在 full_page 长截图里会以视口为基准，导致长图中段出现背景断档留白。
  The background uses a **dedicated layer** filling the whole long image instead of being attached to html/body; a fixed attachment on html/body is viewport-based and leaves blank gaps in full_page screenshots.
- 背景图统一转 **base64 内联**，避免云端 T2I 拉取外链超时。
  Background images are inlined as **base64** to avoid cloud T2I timeouts when fetching external links.
- AstrBot v4.13.0+ 的 file 类型配置，上传文件实际落盘位置随版本不同（**data/plugin_data**、**data/plugins** 等），插件以 data 根为范围做多候选扫描，找不到时回退到插件目录的 **assets/bg.jpg**。
  For file-type configs in AstrBot v4.13.0+, the upload location varies by version; the plugin scans multiple candidate directories and falls back to **assets/bg.jpg**.
- 所有网络 I/O 套用 **asyncio.wait_for** 超时；a2s 字段一律通过 **getattr** 兜底。
  All network I/O is wrapped in **asyncio.wait_for**; a2s fields always use **getattr** fallback.
- 玩家列表查询失败，不影响主信息展示。
  A player-list query failure does not affect the main info display.
- 数据文件 **servers.json** 保存在 AstrBot 的 **data/plugin_data/gmod_a2s_server_query** 目录下，符合持久化数据规范，便于备份、迁移与审计；JSON 读写均使用 try/except 兜底。旧版本遗留在插件目录的 **servers.json** 会在启动时自动迁移。
  The data file **servers.json** is stored under AstrBot's **data/plugin_data/gmod_a2s_server_query**, following the persistence convention for backup, migration and auditing. A legacy **servers.json** left in the plugin directory is migrated automatically on startup.
- 调用自定义 T2I 端点时 **trust_env=False**，不读取环境变量中的代理配置，避免请求被意外转发到未知代理。
  Calls to the custom T2I endpoint use **trust_env=False**, ignoring proxy settings from environment variables so requests are not silently rerouted.

---

## 📁 文件结构 / File Structure

| 文件 / File | 说明 / Description |
|------|------|
| **main.py** | 插件主体（GModServerQuery 类）/ Plugin main body (GModServerQuery class) |
| **metadata.yaml** | 插件元数据（发布信息）/ Plugin metadata for publishing |
| **_conf_schema.json** | 可视化配置项定义（13 项）/ Visual config definitions (13 items) |
| **requirements.txt** | 依赖（python-a2s）/ Dependencies (python-a2s) |
| **.gitignore** | Git 忽略规则 / Git ignore rules |

---

## 🤝 贡献 / 反馈 · Contributing / Feedback

欢迎提交 Issue 或 Pull Request。本插件依赖 [python-a2s](https://pypi.org/project/python-a2s/)（版本 &gt;= 1.4.0）。

Issues and Pull Requests are welcome. This plugin depends on [python-a2s](https://pypi.org/project/python-a2s/) (&gt;= 1.4.0).

---

## 📄 许可证 / License

[MIT License](LICENSE) © yosuki-kata

---

## 📝 更新记录 / Changelog

**版本更新详情，请到 GitHub 仓库查看 / For detailed change history, please visit the GitHub repository.**

> 本插件设计为可长期免维护、长时间不动。若想了解每次发布的具体改动，请前往：
>
> This plugin is designed to be low-maintenance. To see detailed changes for each release, please visit:
>
> **https://github.com/yosuki-kata/astrbot-plugin-gmod-server-query**
