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
- **背景图**：支持上传多张自定义背景图，每次渲染随机选用一张；未配置或图片失效时自动回退插件内置的默认背景图，铺满整张长图不失真。
  **Background**: Upload multiple custom backgrounds and one is picked at random per render; falls back to the bundled default background when unset or missing, filling the entire long image.
- **三级渲染兜底**：内置 T2I → 自定义 T2I → 文字输出，任一渲染服务故障都能给出完整文字总览。
  **Three-level render fallback**: Built-in T2I → Custom T2I → Plain text, always delivering a complete text summary when renderers fail.
- **自定义查询 API**：可接入第三方查询接口作为备用或优先数据源，自动兼容常见字段名；配置后无需改动其他逻辑。
  **Custom query API**: Plug in a third-party query endpoint as a fallback or preferred data source; common field names are auto-detected.
- **LLM 函数工具**：接入 AstrBot 的 LLM 工具调用，模型可直接查询服务器并出图，再按人格自行补一句短评。
  **LLM function tools**: Integrates with AstrBot's LLM tool calling — the model can query a server, send the image, then add its own short remark.
- **服务器组**：管理员可把服务器划分为多个组，成员用 **/gmod list &lt;组名&gt;** 只看该组；一个服务器可同时属于多个组。
  **Server groups**: Admins can group servers; members use **/gmod list &lt;group&gt;** to view only that group. One server may belong to multiple groups.
- **群聊白名单**：可限定仅在指定群聊使用全部功能（私聊不受限制），留空则所有群可用。
  **Group whitelist**: Restrict all features to specified group chats (private chat is always allowed); leave empty to allow every group.
- **可视化配置**：通过 AstrBot 管理面板可视化配置全部选项。
  **Visual config**: All options are configurable from the AstrBot admin panel.

---

## 📦 安装 / Installation

### 方式一：插件市场安装（推荐） / Method 1: AstrBot Plugin Market (recommended)

发布后，直接在 AstrBot 管理面板「**插件市场**」搜索 **gmod**，安装即可，无需处理 zip。

Once published, install directly from the AstrBot admin panel: **Plugin Market → search gmod** and install. No zip handling needed.

### 方式二：手动 zip 安装 / Method 2: Manual zip install

适用于插件市场尚不可用、或你更习惯手动安装的情况。下载本插件仓库的源码压缩包后：

If you prefer a manual install, or the plugin market is not available for you, download the source zip from this repo and:

1. 在 AstrBot 管理面板打开「**插件管理 → 安装**」，上传该 zip 文件。
   In the AstrBot admin panel, open **Plugin Management → Install** and upload the zip.
2. 安装完成后重启插件（或重载插件列表）即可生效。
   Restart the plugin (or reload the plugin list) for it to take effect.

> 无需解压、无需手动改文件名，直接上传即可。
>
> No need to unzip or rename anything — just upload it as-is.

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
**/gmod list &lt;group&gt;**　　　只查看某个服务器组 &middot; Show only one server group
**/gmod help**　　　　　　　　查看帮助 &middot; Show help

群内发送 **&lt;alias&gt;**　　　　直接发别名，自动查询（消息监听，可配置）&middot; Send an alias in group → auto query
群内发送 **&lt;group&gt;**　　　　直接发组名，查看该组服务器列表（消息监听）&middot; Send a group name in group → show that group
群内发送 **[服务器列表]**　　　自动生成列表渲染图 &middot; Auto-generate list render image

### 管理指令（管理员） / Admin commands (administrator)

> 管理功能使用独立的 **gmod-admin 指令组**（不是 **/gmod &lt;xxx&gt;** 子命令形式）。指令必须以 **/gmod-admin** 开头。
>
> Admin features use an **independent gmod-admin command group** (NOT a **/gmod &lt;xxx&gt;** subcommand). You must type the command starting with **/gmod-admin**.

**/gmod-admin add &lt;alias&gt; &lt;IP&gt; [port]**　　添加服务器 &middot; Add a server
**/gmod-admin remove &lt;alias&gt;**　　　　　　　删除服务器 &middot; Remove a server
**/gmod-admin list**　　　　　　　　　　　　　列出现存服务器 &middot; List saved servers

### 服务器组（管理员） / Server groups (administrator)

> 服务器组用于把若干服务器归为一类，成员可用 **/gmod list &lt;组名&gt;** 只看该组的服务器。一个服务器可以同时属于多个组。
>
> **服务器别名与服务器组名必须唯一**：创建时若与另一类重名，插件会提示并拒绝该操作。
>
> Server groups classify your servers. Members can use **/gmod list &lt;group&gt;** to view only that group. One server may belong to multiple groups.
>
> **Alias and group names must be unique**: creating one that collides with the other kind is rejected with a clear message.

**/gmod-admin setgroup &lt;group&gt;**　　　　　　　　创建空组 &middot; Create an empty group
**/gmod-admin addgroup &lt;group&gt; &lt;alias&gt;**　　　把服务器加入组 &middot; Add a server to a group
**/gmod-admin kickgroup &lt;group&gt; &lt;alias&gt;**　　 从组中移出服务器 &middot; Remove a server from a group
**/gmod-admin delgroup &lt;group&gt;**　　　　　　　　删除整个组（服务器本身不删除）&middot; Delete the group (servers are kept)

**示例 / Examples**：

**/gmod-admin setgroup 休闲服**　　　　　　　　　# 创建空组「休闲服」/ Create an empty group
**/gmod-admin addgroup 休闲服 服1**　　　　　　　# 把「服1」加入该组 / Add server to the group
**/gmod-admin addgroup 休闲服 服2**
**/gmod-admin kickgroup 休闲服 服2**　　　　　　　# 把「服2」移出该组 / Remove from the group
**/gmod-admin delgroup 休闲服**　　　　　　　　　# 删除整个组 / Delete the group

指令组与 **/gmod** 的对应关系 / Mapping between the command groups：

| 你想做的事 / What you want | 普通查询指令 / Normal command | 管理指令 / Admin command |
|-----------|------------|---------|
| 查询服务器 / Query server | **/gmod &lt;alias-or-IP&gt;** | — |
| 查看列表 / View list | **/gmod list** | **/gmod-admin list** |
| 查看某个组 / View a group | **/gmod list &lt;group&gt;** | — |
| 添加服务器 / Add server | — | **/gmod-admin add &lt;alias&gt; &lt;IP&gt; [port]** |
| 删除服务器 / Remove server | — | **/gmod-admin remove &lt;alias&gt;** |
| 创建服务器组 / Create group | — | **/gmod-admin setgroup &lt;group&gt;** |
| 组内增删成员 / Group members | — | **/gmod-admin addgroup** / **kickgroup** |
| 删除服务器组 / Delete group | — | **/gmod-admin delgroup &lt;group&gt;** |

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
| **whitelist_groups** | "" | 群聊白名单，留空表示所有群可用；填写后仅这些群可用全部功能（私聊不受限制）。多个群号用逗号或换行分隔 / Group whitelist; empty means all groups allowed. When set, only these groups can use all features (private chat is always allowed). Separate IDs with commas or newlines |
| **query_custom_api** | "" | 自定义查询 API 地址，留空不启用。请求形式为 **GET {地址}?ip={IP}&port={端口}** / Custom query API endpoint; disabled when empty. Requested as **GET {url}?ip={IP}&port={port}** |
| **query_custom_api_key** | "" | 自定义查询 API 密钥，填写后以请求头 **X-API-Key** 发送 / API key sent as the **X-API-Key** header when set |
| **query_custom_api_first** | false | 是否优先使用自定义查询 API（需先填地址）/ Prefer the custom query API (requires an endpoint) |
| **enable_listen** | true | 是否启用消息监听（发别名自动查询）/ Enable message listening (alias auto-query) |
| **listen_only_group** | true | 是否仅在群聊中监听 / Listen only in group chats |
| **listen_exact_match** | true | 仅精确匹配别名，或包含匹配别名 / Exact match or contains match for aliases |
| **render_image** | true | 是否用图片渲染服务器列表 / Render server list as image |
| **render_detail** | true | 是否用图片渲染单服务器详情 / Render single-server detail as image |
| **render_keywords** | ["服务器列表","列表"] | 触发列表渲染图的监听关键词 / Keywords that trigger list render image |
| **render_quality** | 92 | 渲染图 JPEG 画质（1-100，建议 80-95）/ JPEG quality (1-100, suggested 80-95) |
| **render_width** | 1080 | 渲染图输出宽度（px），默认 1080p，可填 1440 / 1920，范围 480-2560 / Render output width in px, default 1080p, 480-2560 |
| **render_background** | [] | 渲染图背景图，支持 jpg/jpeg/png/webp，**上传多张时每次随机选一张**；留空或图片失效时自动回退插件 assets 目录的默认背景，仍无则使用内置渐变 / Background image(s) for rendering; multiple images are picked at random per render, falling back to the bundled assets background and finally a built-in gradient |
| **render_custom_t2i** | "" | 自定义 T2I 服务地址，如 http://127.0.0.1:8000，留空则不启用 / Custom T2I service endpoint, leave empty to disable |
| **prefer_custom_t2i** | false | 是否优先走自定义 T2I（需先填 render_custom_t2i）/ Prefer custom T2I (requires render_custom_t2i) |
| **render_local_t2i** | "" | **【已废弃】** 旧版本地 T2I 地址，请改用 **render_custom_t2i**；留空即可，旧值会被自动读取 / **Deprecated**, use **render_custom_t2i** instead |
| **prefer_local_t2i** | false | **【已废弃】** 旧版优先开关，请改用 **prefer_custom_t2i**；旧值在新项未设置时仍生效 / **Deprecated**, use **prefer_custom_t2i** instead |

> **从 1.1.x 升级 / Upgrading from 1.1.x**
>
> 旧的 **render_local_t2i** / **prefer_local_t2i** 仍可正常工作：当新配置项为空或未设置时，插件会自动读取旧值并输出一条迁移提示日志。你可以在方便时把旧值搬到新字段，然后清空旧字段。
>
> The old **render_local_t2i** / **prefer_local_t2i** keys keep working: when the new keys are empty or unset, the plugin reads the legacy values and logs a one-time migration hint. Move the value to the new fields and clear the old ones whenever convenient.

### 渲染优先级 / Render Priority

插件按以下顺序尝试出图，任一成功即返回：

The plugin tries the following strategies in order and returns on the first success:

| 顺序 | 策略 / Strategy | 说明 / Description |
|------|------|------|
| 1 | 内置 T2I / Built-in T2I | AstrBot 全局配置的 T2I 服务 / The global T2I service configured in AstrBot |
| 2 | 自定义 T2I / Custom T2I | 你在 **render_custom_t2i** 填写的自建或三方服务 / Your own or third-party endpoint in **render_custom_t2i** |
| 3 | 文字输出 / Plain text | 前两者都失败时，输出完整文字总览（含在线玩家名单）/ Falls back to full text summary including player list |

勾选 **prefer_custom_t2i** 后，顺序变为「自定义 T2I → 内置 T2I → 文字输出」。

If **prefer_custom_t2i** is enabled, the order becomes Custom T2I → Built-in T2I → Plain text.

### 查询数据源 / Query Data Source

服务器信息默认通过 A2S 协议直连查询。配置 **query_custom_api** 后，可额外启用第三方接口：

Server data is queried directly over the A2S protocol by default. Once **query_custom_api** is set, a third-party endpoint can be used as well:

| 配置 / Config | 顺序 / Order |
|---|---|
| 未填 query_custom_api / Empty | A2S 直连 → 失败即报错 / A2S only |
| 填了地址，**query_custom_api_first** = false | A2S 直连 → 自定义 API → 报错 / A2S → Custom API |
| 填了地址，**query_custom_api_first** = true | 自定义 API → A2S 直连 → 报错 / Custom API → A2S |

自定义接口返回的字段名会自动多路匹配，包括 **server_name / name / hostname**、**map / map_name**、**players / player_count / numplayers**、**max_players / maxplayers / max** 等，并支持 **data** / **result** 包裹一层的结构。

Field names are auto-detected across common variants such as **server_name / name / hostname**, **map / map_name**, **players / player_count / numplayers**, **max_players / maxplayers / max**, and payloads wrapped in **data** or **result** are also supported.

> **关于自定义 T2I / About Custom T2I**
>
> AstrBot 内置的本地渲染策略不支持自定义 HTML 模板（调用会直接抛 NotImplementedError），因此本插件的「自定义 T2I」需要你自建或准备一个兼容端点。该端点需满足与官方一致的协议：
>
> AstrBot's built-in local strategy does not support custom HTML templates, so the custom T2I here requires a self-hosted or third-party endpoint with the same protocol as the official one:
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
- 渲染链为「内置 T2I → 自定义 T2I → 文字」三级兜底，两路渲染均失败时输出**完整文字总览**（服务器信息 + 在线玩家名单），不会退化为仅有别名清单。
  The render chain has three levels of fallback; when both render paths fail, a **full text summary** (server info + player list) is output instead of a bare alias list.
- 背景图按 **配置项 → assets 目录 → 内置渐变** 三级回退；前两级在多张候选时都随机抽取。配置项里的图片全部定位失败时仍会回退到 assets，避免误删上传文件后无图可用。
  The background falls back through **config → assets → built-in gradient**; the first two levels pick randomly when several candidates exist. If every configured image is missing, it still falls back to assets rather than the gradient.
- 背景图使用**独立背景层**铺满整张长图，而非附着在 html/body 上。若直接给 html/body 用 fixed 附着，在 full_page 长截图里会以视口为基准，导致长图中段出现背景断档留白。
The background uses a **dedicated layer** filling the whole long image instead of being attached to html/body; a fixed attachment on html/body is viewport-based and leaves blank gaps in full_page screenshots.
- 背景图统一转 **base64 内联**，避免云端 T2I 拉取外链超时；读取结果按「路径 + 修改时间 + 大小」缓存，同名图片被替换后会自动失效重读。
  Background images are inlined as **base64** to avoid outbound image fetches timing out on cloud T2I; results are cached by path + mtime + size, and the cache invalidates automatically when the file is replaced.
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
- 自定义查询 API 同样使用 **trust_env=False**，请求失败时按配置顺序回退到另一条链路，不会因为接口不可用而让查询整体失败。
  Custom query API calls also use **trust_env=False**; a failure falls back to the other data source, so an unavailable endpoint never breaks the query entirely.
- LLM 工具只读：仅注册 **gmod_list_servers** 与 **gmod_query_server**，不含添加/删除，避免模型误改服务器数据。
  LLM tools are read-only: only **gmod_list_servers** and **gmod_query_server** are registered, no add/remove, so the model cannot modify saved data.
- LLM 工具把渲染图通过 **send_message** 直接发给用户，返回值只带一行紧凑摘要给模型，避免用户收到图后又看到一遍重复的数据文本。
  The LLM tool sends the rendered image to the user via **send_message** and returns only a compact one-line summary to the model, so the user doesn't get the same data twice.

---

## ⚠️ 免责声明 / Disclaimer

本插件提供两个可选的「外部端点」配置：**自定义 T2I 服务**与**自定义查询 API**。两者的地址全部由使用者自行填写，插件本体不对其行为负责。

This plugin offers two optional external endpoints: a **custom T2I service** and a **custom query API**. Both addresses are supplied by the user; the plugin takes no responsibility for their behavior.

### 一、自定义 T2I 服务 / Custom T2I Service

1. 该端点地址完全由你提供，作者不提供、不托管、也不推荐任何具体的第三方端点。
   The endpoint is entirely your own choice; the author does not provide, host, or endorse any specific third-party endpoint.
2. 渲染时，插件会把服务器信息（名称、地图、在线人数、玩家名单等）与渲染模板一并 **POST** 到你填写的地址。
   During rendering, the plugin **POSTs** server data (name, map, player count, player list, etc.) together with the render template to the address you configured.
3. 请确保该服务来源可信。若地址被替换为恶意或不可控的服务，你的服务器与玩家信息可能会被第三方获取。
   Please make sure the service is trustworthy. A malicious or uncontrolled endpoint could collect your server and player data.
4. 插件无法审查、也无法限制自配端点的实际行为，一切后果由配置者自行承担。
   The plugin cannot audit or restrict what a self-configured endpoint actually does; the configurator bears all consequences.

### 二、自定义查询 API / Custom Query API

1. 该接口地址与密钥完全由你提供，作者不对其可用性、准确性或安全性作任何保证。
   The endpoint and key are entirely your own; the author makes no guarantee about availability, accuracy, or security.
2. 查询时，插件会以 **GET** 方式把你所查询服务器的 **IP 与端口**发送到你填写的地址。
   When querying, the plugin **GETs** your configured address and sends the server's **IP and port**.
3. 请确保该服务来源可信。第三方接口可能会记录、转发或滥用你提交的服务器信息。
   Please make sure the service is trustworthy; a third-party endpoint may log, forward, or misuse the server information you submit.
4. 插件无法审查、也无法限制自配接口的实际行为，一切后果由配置者自行承担。
   The plugin cannot audit or restrict what a self-configured endpoint actually does; the configurator bears all consequences.

> **一句话总结 / In short**：配置什么地址，数据就发到哪里。请自行判断并承担风险。
>
> **What you configure is where your data goes.** Judge accordingly and accept the risk.

---

## 📁 文件结构 / File Structure

| 文件 / File | 说明 / Description |
|------|------|
| **main.py** | 插件主体，全部逻辑集中在此文件 / Plugin entry point, all logic lives here |
| **metadata.yaml** | 插件元数据（名称、作者、版本等发布信息）/ Plugin metadata for publishing |
| **_conf_schema.json** | 可视化配置项定义 / Visual config definitions |
| **requirements.txt** | 运行依赖（python-a2s）/ Runtime dependencies (python-a2s) |
| **assets/** | 内置默认背景图，可放入多张（bg.jpg / 1.png 等）随机轮换 / Bundled default backgrounds; drop in several images to rotate |
| **CHANGELOG.md** | 完整版本变更记录（按版本降序）/ Full version history, newest first |
| **logo.png** | 插件市场图标（256×256，1:1）/ Plugin market icon (256x256, 1:1) |

---

## 🤝 贡献 / 反馈 · Contributing / Feedback

欢迎提交 Issue 或 Pull Request。本插件依赖 [python-a2s](https://pypi.org/project/python-a2s/)（版本 &gt;= 1.4.0）。

Issues and Pull Requests are welcome. This plugin depends on [python-a2s](https://pypi.org/project/python-a2s/) (&gt;= 1.4.0).

---

## 📄 许可证 / License

[MIT License](LICENSE) © yosuki-kata

---

## 📝 更新记录 / Changelog

**完整版本变更记录见 [CHANGELOG.md](CHANGELOG.md)（按版本降序）。** / **See [CHANGELOG.md](CHANGELOG.md) for the full version history (descending order).**

> 本插件设计为可长期免维护、长时间不动。若想了解每次发布的具体改动，请前往：
>
> This plugin is designed to be low-maintenance. To see detailed changes for each release, please visit:
>
> **https://github.com/yosuki-kata/astrbot-plugin-gmod-server-query**
