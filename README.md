# 🎮 gmod服务器查询插件：重制 · GMod Server Query Plugin

![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **一个面向 AstrBot 的 Garry's Mod (GMod) 服务器在线查询插件（重制版 v1.0.1）。**
> >
> **An online server query plugin for Garry's Mod (GMod) running on AstrBot (remastered v1.0.1).**

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
- **列表渲染图**：发送「服务器列表」或运行 **/gmod list** 时，生成高画质 JPEG 列表图片（画质可配置）。
  **List render image**: Sending "服务器列表" or running **/gmod list** generates a high-quality JPEG list image (quality configurable).
- **可视化配置**：通过 AstrBot 管理面板可视化配置全部选项。
  **Visual config**: All options are configurable from the AstrBot admin panel.

---

## 📦 安装 / Installation

### 方式一：插件市场安装（推荐） / Method 1: AstrBot Plugin Market (recommended)

发布后，直接在 AstrBot 管理面板「**插件市场**」搜索 **gmod**，安装即可，无需处理 zip。

Once published, install directly from the AstrBot admin panel: **Plugin Market → search gmod** and install. No zip handling needed.

### 方式二：手动 zip 安装 / Method 2: Manual zip install

> **压缩包命名规范 / Zip naming rule**：成品压缩包须命名为 **V主版本号.次版本号.修订版本号.zip**（如 **V1.0.1.zip**），并与 **metadata.yaml** 中的 **version** 字段严格一致。其他命名（如 **插件_v1.0.zip**）不推荐。
>
> The final package must be named **V&lt;major&gt;.&lt;minor&gt;.&lt;patch&gt;.zip** (e.g. **V1.0.1.zip**), strictly matching the **version** field in **metadata.yaml**. Other names (like **插件_v1.0.zip**) are NOT recommended.

步骤 / Steps：

1. 打包为 **V1.0.1.zip**，将 **main.py**、**metadata.yaml**、**_conf_schema.json**、**requirements.txt** 放在 zip 根目录（不要放进子文件夹）。
   Create the zip: **V1.0.1.zip**, with **main.py**, **metadata.yaml**, **_conf_schema.json**, **requirements.txt** at the zip root (not inside a sub-folder).
2. 在 AstrBot 管理面板「**插件管理 → 安装**」上传 zip。
   In the AstrBot admin panel: **Plugin Management → Install → upload the zip**.
3. 安装完成后，重启插件即可生效。
   Restart the plugin for it to take effect.

> **metadata.yaml** 必须使用官方字段（**name**、**display_name**、**version**、**author**、**repo**、**astrbot_version**、**tags** 等）。
> **metadata.yaml** must use the official fields (**name**, **display_name**, **version**, **author**, **repo**, **astrbot_version**, **tags**, ...).

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
| **render_keywords** | ["服务器列表","列表"] | 触发列表渲染图的监听关键词 / Keywords that trigger list render image |
| **render_quality** | 92 | 列表渲染图 JPEG 画质（1-100，建议 80-95）/ JPEG quality of list render image (1-100, suggested 80-95) |

---

## 🔧 技术要点 / Technical Notes

- 列表渲染图**不传数字 scale**，用 **quality + full_page** 控制清晰度（规避云端 T2I 的 HTTP 422）。
  The list render image does **NOT** pass a numeric **scale**; it uses **quality + full_page** for sharpness (avoids cloud T2I HTTP 422).
- **html_render** 对旧版无 **options** 参数的版本，做了 **TypeError 兼容回退**。
  **html_render** has a **TypeError fallback** for older versions without the **options** parameter.
- 所有网络 I/O 套用 **asyncio.wait_for** 超时；a2s 字段一律通过 **getattr** 兜底。
  All network I/O is wrapped in **asyncio.wait_for**; a2s fields always use **getattr** fallback.
- 玩家列表查询失败，不影响主信息展示。
  A player-list query failure does not affect the main info display.
- 数据文件 **servers.json** 的路径相对于插件目录；JSON 读写均使用 try/except 兜底。
  The data file **servers.json** path is relative to the plugin directory; JSON read / write uses try / except fallback.

---

## 📁 文件结构 / File Structure

| 文件 / File | 说明 / Description |
|------|------|
| **main.py** | 插件主体（GModServerQuery 类）/ Plugin main body (GModServerQuery class) |
| **metadata.yaml** | 插件元数据（发布信息）/ Plugin metadata for publishing |
| **_conf_schema.json** | 可视化配置项定义（8 项）/ Visual config definitions (8 items) |
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
