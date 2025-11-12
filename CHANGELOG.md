# 更新日志 / Changelog

本文档记录本插件的历次版本变更，**最新版本在最上方**。
All notable changes to this plugin are documented here, **newest first**.

---

## [1.2.1] - 未发布 / Unreleased

### 新增功能 / Added

- **服务器分组建管理**：服务器多了之后，可以用分组把它们的安排清楚。一个服务器可以同时放进多个分组，比如既属于「日常服」也属于「比赛服」。
  **Server groups**: When you have many servers, groups keep them organized. One server can belong to several groups at once — say, both "daily" and "competitive".
- **按分组查看**：`/gmod list 分组名` 只看这个分组里的服务器；`/gmod 分组名` 也一样。在群里直接说分组名，同样会自动把这一组的状态图发出来，跟直接说服务器别名一样方便。
  **View by group**: `/gmod list <group>` shows only that group, and `/gmod <group>` works too. Saying a group name in chat automatically sends that group's status image, just like saying a server alias.
- **指定群聊使用**：可以设置只在某些群里响应本插件。不填就是所有群都能用；私聊任何时候都不受影响。
  **Limit to specific groups**: You can restrict the plugin to certain group chats. Leave it empty and every group works; private chat is never affected.
- **名称不能重复**：服务器别名和分组名不允许撞名。撞了会直接告诉你哪里冲突、并拒绝这次操作，不会出现「叫了个名字却不知道查的是哪个」的情况。
  **Unique names**: Server aliases and group names cannot collide. If they do, the plugin tells you exactly what conflicts and refuses the operation, so you never end up unsure which one a name refers to.

### 改进 / Changed

- **老数据自动升级**：新增分组后，原来的服务器数据不用手动处理，插件会自己识别并升级格式，一个都不会丢。
  **Automatic data upgrade**: Existing server data needs no manual work — the plugin detects and upgrades the format on its own, losing nothing.
- **删除服务器更干净**：删掉一台服务器时，它也会自动从所有分组里移出，不会在分组里留下一个点进去查不到的空名。
  **Cleaner removal**: Deleting a server also removes it from every group, so no empty names are left behind.
- **分组内容自动校验**：查看分组时，已经失效的服务器会被自动跳过；整组都没有可用服务器时会直接说明，而不是给你一个空列表。
  **Group validation**: Invalid servers are skipped when viewing a group, and you get a clear message instead of an empty list when a group has nothing usable.
- **AI 功能更懂事**：接入 AI 助手后，它现在知道有哪些分组，也能理解你说「看看日常服」这类话，直接把整组状态发给你。
  **Smarter AI integration**: With the AI assistant connected, it knows your groups and understands requests like "show me the daily servers", sending the whole group's status directly.
- **提示文案优化**：分组相关的各种情况都有对应的说明，不再出现让人摸不着头脑的报错。
  **Better messages**: Group-related situations now all have clear explanations instead of confusing errors.

### 文档 / Documentation

- 补充了分组与群聊限定的使用说明。
  Added usage docs for groups and group restrictions.
- 新增本更新日志。
  Added this changelog.

---

## [1.2.0] - 2026-11-08

### 新增功能 / Added

- **自定义查询接口**：如果你的服务器用的查询服务比较特殊，或者想接第三方接口，现在可以自己填一个地址。插件会自动适应不同接口返回的数据格式，不用你手动调整。接口临时不可用时会自动改用另一条路，查询不会因此失败。
  **Custom query endpoint**: If your server uses an unusual query service, or you want to plug in a third-party API, you can now supply your own address. The plugin adapts to different response formats automatically, and if the endpoint is temporarily down it falls back to another route so queries never fail.
- **AI 助手直接查询**：接上 AstrBot 的 AI 能力后，你可以直接问「XXX 服现在几个人」，它会自己去查、把状态图发出来，还能顺口点评一句。图片由插件发送，不会让 AI 把数据再啰嗦地重复一遍。
  **AI assistant querying**: With AstrBot's AI connected, just ask "how many people are on server X" — it queries by itself, sends the status image, and may add a short comment. The image is sent by the plugin, so the AI does not repeat the data.
- **插件图标**：插件市场里现在有专属图标了。
  **Plugin icon**: The plugin now has its own icon in the market.

### 改进 / Changed

- **配置项名称调整**：原来叫「本地 T2I 地址」的两项改成了「自定义 T2I 服务地址」。因为「本地」这个词容易让人以为只能填 127.0.0.1，实际上填任何地址都行。老配置照样能用，插件会自动读取旧值并提示一次，不需要手动改。
  **Renamed options**: The two "local T2I" options are now "custom T2I service". The word "local" made people assume only 127.0.0.1 was allowed, while any address works. Old settings keep working — the plugin reads the previous values and shows a one-time hint, no manual edits needed.
- **状态图加载更快**：内置背景图体积减了 79%，分辨率完全没变，肉眼几乎看不出区别。出图速度和中转流量都有明显改善。
  **Faster status images**: The bundled background is 79% smaller with identical resolution and virtually no visible difference, improving both render speed and transfer size.
- **市场简介更清爽**：市场卡片改用一句话简介，在手机上看起来更舒服。
  **Cleaner market listing**: The market card now uses a one-line summary that reads better on mobile.

### 修复 / Fixed

- 修复 AI 助手发图时报错、图片发不出去的问题。
  Fixed an error that prevented the AI assistant from sending images.
- 修复自定义查询接口返回的在线人数格式不标准时，人数被错误显示为 0 的问题。
  Fixed player counts showing as 0 when the custom query endpoint returned an unusual format.

### 文档 / Documentation

- 新增免责声明，分别说明自定义文转图服务和自定义查询接口会把数据发到哪里，提醒你确认所填地址是否可信。
  Added a disclaimer explaining where the custom text-to-image service and custom query endpoint send your data, and reminding you to verify those addresses are trustworthy.
- 补充查询数据源说明与配置项说明。
  Expanded the query data source and configuration documentation.

---

## [1.1.0] - 2026-11-07

### 新增功能 / Added

- **多背景图随机切换**：现在可以上传多张背景图，每次出图随机选一张，不再是永远同一个背景。直接把多张图片丢进 assets 目录也能生效，不用改文件名。
  **Random background rotation**: Upload several backgrounds and one is picked at random for each render instead of always using the same one. Dropping extra images into the assets folder also works — no renaming needed.
- **背景图失效不再变光板**：如果配置的背景图被误删或找不到，会自动改用插件自带的背景，而不是直接掉成一片空白。两者都没有时才使用内置渐变。
  **Graceful background fallback**: If your configured background is deleted or missing, the bundled one is used instead of dropping to a blank canvas. The built-in gradient only appears when neither is available.

### 改进 / Changed

- **数据存放位置规范化**：服务器配置改为保存在 AstrBot 官方推荐的数据目录，重装或升级插件时不会再丢数据。
  **Standard data location**: Server config now lives in AstrBot's official data directory, so reinstalling or upgrading the plugin no longer loses it.
- **旧数据自动搬移**：升级后如果发现旧位置还有数据，会自动复制到新位置，你不需要手动处理。
  **Automatic data migration**: If data is found in the old location after an upgrade, it is copied to the new one automatically.
- **出图更稳定**：修复了背景图被替换后仍显示旧图的问题，同时减少了大图反复读取带来的卡顿。
  **More stable rendering**: Fixed replaced backgrounds still showing the old image, and reduced stutter from repeatedly reading large images.

---

## [1.0.4] - 2026-11-06

### 新增功能 / Added

- **单服详情图**：查询单台服务器时，会生成一张详情卡片，除了基本状态还包含玩家名单和服务器参数。
  **Single-server detail card**: Querying one server produces a detail card with the player list and server properties in addition to basic status.
- **出图失败也有内容**：图片渲染服务出问题时，会自动改用完整的文字信息，不会出现「发了指令什么都没回」的情况。
  **Text fallback on render failure**: When image rendering fails, the plugin switches to full text information, so a command never returns nothing.
- **自定义文转图服务**：可以接入自己的图片渲染服务，作为内置方案的替代或补充。
  **Custom text-to-image service**: You can plug in your own image rendering service as a replacement or supplement to the built-in one.
- **失败原因更明确**：出图失败时会区分是渲染服务的问题还是其他原因，告诉你去检查哪里。
  **Clearer failure reasons**: Render failures now distinguish rendering-service problems from other causes and point you where to look.

### 改进 / Changed

- **可自定义出图**：新增单服详情图开关、输出宽度（默认 1080p，可调更高清）和自定义背景图。
  **Configurable output**: Added a detail-card toggle, output width (1080p by default, can go higher) and custom backgrounds.
- **列表图与详情图风格统一**：两种图片使用同一套样式，信息排版保持一致。
  **Consistent styling**: List and detail images now share one style with matching layout.

---

## [1.0.3] - 2026-11-05

### 安全 / Security

- **管理指令加了权限校验**：添加、删除、查看服务器这几条指令之前没有校验身份，群里任何人都能修改服务器配置。现在只有管理员可以使用，其他人执行会收到提示。
  **Admin permission checks**: The add, remove and list commands had no identity check, so anyone in a group could modify server config. They are now admin-only, and others receive a notice.

### 改进 / Changed

- 优化了插件元数据的结构稳定性。
  Improved the structural stability of plugin metadata.
- 补充了版本控制忽略规则。
  Added ignore rules to version control.

---

## [1.0.2] - 2026-11-04

### 修复 / Fixed

- 修复从插件市场安装时加载失败、被自动回滚的问题（事件监听相关的导入冲突）。
  Fixed installation from the plugin market failing to load and being rolled back (an import conflict involving event listeners).
- 修复新版 AstrBot 下插件注册方式不兼容导致的安装失败。
  Fixed an installation failure caused by an incompatible registration method on newer AstrBot versions.

### 改进 / Changed

- 调整了插件标签分类，在插件市场里更容易被搜到。
  Adjusted plugin tags so it is easier to find in the market.

---

## [1.0.1] - 2026-11-04

### 修复 / Fixed

- 移除了一个已废弃的导入，解决从插件市场安装时加载失败并被回滚的兼容性问题。
  Removed a deprecated import, fixing a compatibility issue where installation from the plugin market failed to load and was rolled back.

---

## [1.0.0] - 2026-11-03

### 新增功能 / Added

- **首个重制版本**：基于原 v3.3.2 的全部功能彻底重写，结构更清晰。
  **First rewritten release**: A complete rewrite of everything in the original v3.3.2, with a clearer structure.
- **别名管理**：把服务器 IP 和端口存成好记的名字，以后直接说名字就行。
  **Alias management**: Save a server's IP and port under an easy name and just say the name afterwards.
- **服务器查询**：查某台服务器的在线人数、当前地图、延迟等信息，可以直接输 IP，也可以输别名。
  **Server query**: Check player count, current map, latency and more — by IP or by alias.
- **超时保护**：网络查询设有超时，不会因为服务器没响应就卡住不动。
  **Timeout protection**: Network queries time out instead of hanging when a server does not respond.
- **群里自动响应**：在群里直接说服务器名字，就会自动查询，不用每次都打指令。
  **Auto-response in chat**: Say a server name in the group and it queries automatically — no command needed.
- **状态一览图**：一次生成所有服务器的状态图片，一目了然。
  **Status overview image**: Generates one image showing every server's status at a glance.
- **自定义背景**：可以上传自己喜欢的背景图，铺满整张长图且不失真。
  **Custom background**: Upload your own background; it fills the whole long image without distortion.
- **可视化配置**：所有选项都能在 AstrBot 管理面板里直接设置。
  **Visual config**: Every option is configurable right from the AstrBot admin panel.