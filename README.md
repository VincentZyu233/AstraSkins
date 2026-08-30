> **[📖 English](README.en-us.md)**
> **[📖 简体中文(大陆)](README.md)**

<div align="center">

# 🎨 Astra Skins

[![上游仓库](https://img.shields.io/badge/GitHub-Upstream%20Repository-181717?logo=github&style=for-the-badge)](https://github.com/Ayrton09/AstraSkins)

**为 Counter-Strike 2 提供武器皮肤、刀具、手套和探员，并内置 WASD 菜单、玩家独立自定义和数据库持久化。**

[![CS2](https://img.shields.io/badge/game-Counter--Strike%202-orange)](https://www.counter-strike.net/)
[![CounterStrikeSharp](https://img.shields.io/badge/CounterStrikeSharp-%E2%89%A5%201.0.369-blue)](https://github.com/roflmuffin/CounterStrikeSharp)
[![.NET](https://img.shields.io/badge/.NET-10-512BD4)](https://dotnet.microsoft.com/)
[![CI](https://github.com/Ayrton09/AstraSkins/actions/workflows/ci.yml/badge.svg)](https://github.com/Ayrton09/AstraSkins/actions/workflows/ci.yml)
[![许可证](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

---

## ✨ 功能特性

- 🎨 **1,400+ 款武器皮肤、20 种刀具及其 576 款外观、8 种手套、63 名探员** — 全部由 JSON 数据驱动，代码中不内置数据集。
- 🕹️ **内置 WASD 菜单** — 使用 `W`/`S` 导航，按 `E` 选择，无需外部菜单插件。
- 🔧 **玩家独立自定义** — 可通过 `!seed`、`!wear`、`!nametag` 和 `!stattrak` 自定义图案模板、磨损度、名称标签及 StatTrak 计数。
- 🔎 **搜索** — 使用 `!ws <文本>` 即可查找任意皮肤、刀具、手套或探员，无需逐页浏览。
- 💾 **持久化选择** — 支持 SQLite 或 MySQL，以 SteamID64 为键；重连、换图和重启后选择仍会保留。
- 🌍 **7 种语言** — 按玩家提供本地化（英语、西班牙语、中文、葡萄牙语、德语、法语、俄语）。
- 🗣️ **探员无线电语音** — 当 CS2 schema 提供语音数据时，探员会保留其语音台词。
- 🛡️ **权限控制** — 可将单个皮肤、刀具、手套、探员或整个自定义功能限制为指定管理员权限。
- ⚙️ **管理工具** — 支持热重载定义和诊断命令。

## 📋 环境要求

- [CounterStrikeSharp](https://github.com/roflmuffin/CounterStrikeSharp) `1.0.369` 或更高版本（配合 Metamod:Source），运行于 `.NET 10`。
- SQLite（无需配置）或 MySQL 服务器，需在配置中明确选择。

## 📦 安装

1. 在 CS2 专用服务器上安装 [Metamod:Source](https://www.sourcemm.net/) 和 [CounterStrikeSharp](https://docs.cssharp.dev/docs/guides/getting-started.html)。
2. **必需：**编辑 `addons/counterstrikesharp/configs/core.json` 并设置：

   ```json
   "FollowCS2ServerGuidelines": false
   ```

   若不这样设置，CounterStrikeSharp 会阻止本插件所需的物品属性写入，**任何皮肤都不会生效**。
3. 按以下目录结构复制插件文件：

   ```text
   addons/
     counterstrikesharp/
       plugins/
         AstraSkins/
           AstraSkins.dll
           AstraSkins.deps.json
           data/            ← 武器、刀具、手套、探员、分类 JSON
           lang/            ← 翻译文件
           schema/          ← 参考 SQL（插件会自行建表）
       gamedata/
         astra_skins.json   ← 必需，参见下方“游戏数据”
       configs/
         plugins/
           AstraSkins/
             AstraSkins.json
   ```

4. 在 `configs/plugins/AstraSkins/AstraSkins.json` 中配置数据库（参见[配置](#配置)）。SQLite 开箱即用；MySQL 需要预先存在的数据库和用户。
5. 重启服务器（或执行 `css_plugins load AstraSkins`）。启动日志会报告加载的皮肤、刀具、手套和探员数量。

## ⌨️ 命令

### 👤 玩家命令

| 命令 | 说明 |
| --- | --- |
| `!ws` | 打开主皮肤菜单 |
| `!ws <搜索内容>` | 同时搜索所有皮肤、刀具、手套和探员 |
| `!knife` | 打开刀具菜单 |
| `!gloves` | 打开手套菜单 |
| `!agents` | 打开探员菜单 |
| `!wsrefresh` | 重新应用已保存的选择 |
| `!wsreset [all\|weapons\|knife\|gloves\|agents]` | 重置全部或指定分类的已保存选择 |

### 🎨 自定义

| 命令 | 说明 |
| --- | --- |
| `!seed <0-1000>` | 设置手持武器的自定义图案模板 · 使用 `!seed gloves <n>` 设置手套 · 使用 `!seed reset` 清除 |
| `!wear <0.00-1.00>` | 设置手持武器的自定义磨损度 · 使用 `!wear gloves <n>` 设置手套 · 使用 `!wear reset` 清除 |
| `!nametag <文本>` | 设置手持武器的名称标签 · 使用 `!nametag reset` 移除 |
| `!stattrak` | 切换手持武器的 StatTrak · `!stattrak <计数>` 设置计数器 · `!stattrak reset` 移除 |

自定义项会叠加在已选皮肤之上，立即生效并持久化到数据库。默认目标是当前手持武器（包括刀具）；将 `gloves` 作为第一个参数即可改为已装备的手套。使用前必须先为该物品选择皮肤。

StatTrak 的工作方式相同：在武器或刀具上启用后，每次使用该物品击杀都会增加计数，并在重连和换图后继续保留。

> **提示：**图案模板只会改变图案位置可变的外观，例如表面淬火、深红之网、大理石渐变和渐变之色。大多数其他皮肤在不同模板下看起来完全相同。

### 🛡️ 管理员命令

| 命令 | 默认权限 | 说明 |
| --- | --- | --- |
| `!wsreload` | `@css/config` | 重载 JSON 定义并为所有玩家重新应用皮肤 |
| `!wsdebug` | `@css/config` | 显示诊断信息：加载数量、数据库模式及调用者的选择 |

这两个命令都可以在配置中完全禁用。

## 🎮 菜单操作

| 按键 | 操作 |
| --- | --- |
| `W` / `S` | 上移 / 下移 |
| `E` | 选择 |
| `Shift` | 返回 |
| `R` | 关闭 |

菜单项目带有编号，仅作为辨认位置的视觉提示；实际使用按键而非数字导航。菜单打开时玩家会被固定在原地。请注意：`E` 仍会执行游戏世界中的常规动作（开门、拾取武器、拆弹），因此站在炸弹上时不要确认选择。

## 🔍 搜索

仅武器皮肤就有 1,449 款，逐页浏览并不总是最快的方式。`!ws <搜索内容>` 会打开一个扁平结果列表，涵盖武器皮肤、刀具外观、手套外观和探员。

每个以空格分隔的词都必须出现在条目中，因此可以快速缩小范围：

```text
!ws redline        → 所有拥有 Redline 的武器
!ws ak redline     → 直接找到 AK-47 Redline
!ws marble fade    → 所有 Marble Fade 刀具
!ws ct mccoy       → 对应的 CT 探员
```

搜索结果会遵守权限限制，最多显示 64 项；已经装备的物品会以 `*` 标记。

## ⚙️ 配置

`configs/plugins/AstraSkins/AstraSkins.json` — 默认配置可安全公开，并使用占位凭据：

```json
{
  "ConfigVersion": 1,
  "DatabaseMode": "mysql",
  "Sqlite": {
    "Path": "data/astra_skins.sqlite"
  },
  "MySql": {
    "Host": "127.0.0.1",
    "Port": 3306,
    "Database": "astra_skins",
    "Username": "astra_skins",
    "Password": "change-me",
    "SslMode": "required"
  },
  "Menu": {
    "ItemsPerPage": 6,
    "TimeoutSeconds": 25,
    "CooldownMilliseconds": 180,
    "SelectionCooldownMilliseconds": 900,
    "AllowWhileDead": true
  },
  "Customization": {
    "Enabled": true,
    "Permission": "",
    "MaxNameTagLength": 20
  },
  "Definitions": {
    "Weapons": "data/weapons.json",
    "Knives": "data/knives.json",
    "Gloves": "data/gloves.json",
    "Agents": "data/agents.json",
    "Categories": "data/categories.json"
  },
  "EnableAdminReloadCommand": true,
  "AdminReloadPermission": "@css/config",
  "EnableAdminDebugCommand": true,
  "AdminDebugPermission": "@css/config"
}
```

| 配置项 | 作用 |
| --- | --- |
| `DatabaseMode` | `"sqlite"` 或 `"mysql"` — 必填，启动时验证 |
| `Menu.ItemsPerPage` | 可见菜单行数（3–6） |
| `Menu.TimeoutSeconds` | 菜单空闲多少秒后自动关闭 |
| `Menu.CooldownMilliseconds` | 菜单按键之间的最短延迟 |
| `Menu.SelectionCooldownMilliseconds` | 皮肤选择之间的最短延迟 |
| `Menu.AllowWhileDead` | 是否允许死亡时打开菜单 |
| `Customization.Enabled` | `!seed` / `!wear` / `!nametag` 的总开关 |
| `Customization.Permission` | 将自定义限制为某项权限；留空 = 所有人 |
| `Customization.MaxNameTagLength` | 名称标签长度上限，4–32（默认 20，与游戏实际限制一致） |

### 🗃️ SQLite

```json
{ "DatabaseMode": "sqlite", "Sqlite": { "Path": "data/astra_skins.sqlite" } }
```

插件会在启动时创建 schema，无需安装任何内容。请注意，默认路径位于插件目录内部：**重新部署插件目录前请备份 `.sqlite` 文件**，或者将 `Path` 指向目录外部。

### 🛢️ MySQL

```json
{ "DatabaseMode": "mysql", "MySql": { "Host": "…", "Port": 3306, "Database": "astra_skins", "Username": "astra_skins", "Password": "…", "SslMode": "required" } }
```

数据库和用户必须预先存在；插件会在启动时创建数据表。`SslMode` 可使用 `none`、`preferred`、`required`（默认）、`verifyca` 或 `verifyfull` — 远程数据库应保持 `required`，确保凭据加密传输；仅当 MySQL 服务器禁用 TLS 时才使用 `preferred` 或 `none`。

## 🌐 本地化

所有面向玩家的消息和菜单标签都会通过 CounterStrikeSharp 的语言系统按玩家本地化。玩家可使用 `css_lang <语言>` 选择语言（例如 `css_lang es`）；缺失翻译会回退到服务器语言。

内置语言：`en` 英语 · `es` 西班牙语 · `zh` 简体中文 · `pt` 葡萄牙语 · `de` 德语 · `fr` 法语 · `ru` 俄语 — 均为 `lang/` 中的扁平键值 JSON 文件。

发现错误或缺失的翻译？欢迎提交 PR — 编辑对应的 `lang/*.json` 即可。若要添加语言，请将 `en.json` 复制为 `<culture>.json` 并翻译其中的值。

## 🎭 饰品数据

所有饰品内容都位于 `data/*.json`，并在启动及执行 `!wsreload` 时验证；格式错误的 JSON、重复 ID、未知武器实体、缺失字段和损坏的分类引用都会被跳过，并留下清晰的日志消息。

当前打包内容：

| 类型 | 数量 |
| --- | ---: |
| 武器 | 34 |
| 武器皮肤 | 1,449 |
| 刀具 | 20 |
| 刀具皮肤 | 576 |
| 手套类型 | 8 |
| 手套皮肤 | 94 |
| 探员 | 63 |

若要在 CS2 更新后重新生成数据，请运行内置生成器，它会自动拉取最新的 `items_game.txt` 和翻译数据：

```bash
python tools/generate_definitions.py --output data
```

## 🧩 游戏数据

将 `gamedata/astra_skins.json` 复制到 `addons/counterstrikesharp/gamedata/`。其中包含用于以可视方式应用涂装属性的唯一内存签名。

CS2 更新可能导致该签名失效。发生这种情况时，插件会继续运行并记录清晰的错误，而不会崩溃；更新签名（或获取更新后的发行版）即可恢复皮肤渲染。

## 🔨 从源代码构建

```bash
dotnet build -c Release
```

需要 .NET 10 SDK。可部署输出位于 `src/AstraSkins/bin/Release/net10.0/`。

## 🛠️ 故障排查

| 症状 | 解决方法 |
| --- | --- |
| 皮肤始终不生效，且没有错误 | 在 `configs/core.json` 中设置 `FollowCS2ServerGuidelines: false` 并重启 |
| 日志中出现“gamedata signature is missing” | 将 `gamedata/astra_skins.json` 复制到 `addons/counterstrikesharp/gamedata/` |
| CS2 更新后皮肤停止工作 | gamedata 签名已失效 — 参见[游戏数据](#游戏数据) |
| `!wsreload` / `!wsdebug` 提示无权限 | 在 `configs/admins.json` 中添加你的 SteamID，并授予 `@css/config` 权限 |
| `!seed` 看起来没有效果 | 手持皮肤的图案不会随模板变化 — 请尝试 Case Hardened 或 Crimson Web |

## ⚠️ 免责声明

服务端皮肤插件与 Valve 的[服务器准则](https://blog.counter-strike.net/index.php/server_guidelines/)存在冲突。在使用 GSLT 的公共服务器上运行本插件会带来令牌被封禁的风险，服务器运营者需自行承担。请谨慎使用。

## 📄 许可证

[MIT](LICENSE) © Ayrton
