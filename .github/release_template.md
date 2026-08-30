<div align="center">

[![下载量](https://img.shields.io/github/downloads/__REPO__/__VERSION__/total?style=flat-square&logo=github)](https://github.com/__REPO__/releases/tag/__VERSION__)
[![CS2](https://img.shields.io/badge/适用于-Counter--Strike%202-FFB71E?style=flat-square)](https://developer.valvesoftware.com/wiki/Counter-Strike_2/Dedicated_Servers)
[![.NET](https://img.shields.io/badge/.NET-10-512BD4?style=flat-square&logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)

</div>

---

### ⬇️ 下载

| 文件 | 用途 |
| --- | --- |
| [📦 `AstraSkins-__VERSION__.zip`](__BASE_URL__/AstraSkins-__VERSION__.zip) | **推荐**：完整可部署包，包含 DLL、依赖、数据、语言文件、gamedata 和默认配置 |
| [🔌 `AstraSkins-__VERSION__.dll`](__BASE_URL__/AstraSkins-__VERSION__.dll) | 插件主二进制，仅供校验或高级用户手动更新 |
| [🐛 `AstraSkins-__VERSION__.pdb`](__BASE_URL__/AstraSkins-__VERSION__.pdb) | 调试符号，可保留异常堆栈行号 |

> **请优先使用完整 zip。** 独立 DLL 不能替代 `deps.json`、依赖库、`data/`、`lang/`、`schema/` 和 `gamedata/`；缺少这些文件时插件无法完整工作。

### 📥 安装

1. 安装 Metamod:Source 和 CounterStrikeSharp `1.0.369` 或更高版本。
2. 下载并解压完整 zip 到 CS2 的 `game/csgo/` 目录。
3. 在 CounterStrikeSharp 的 `core.json` 中设置 `FollowCS2ServerGuidelines: false`。
4. 配置 `addons/counterstrikesharp/configs/plugins/AstraSkins/AstraSkins.json`。
5. 重启服务器，或在无人使用插件菜单时重载 AstraSkins。

### ✨ 本次更新

- 新增 Zeus x27 电击枪及 7 款官方皮肤，支持固定主菜单入口、分类浏览和中英文搜索。
- Zeus 皮肤选择原地应用，不销毁已持有实体，并使用正确的 `slot11` 恢复活动武器。
- README badge、双语文档数量和 GitHub Release 自动发布流程同步更新。

### 🧾 构建信息

- 构建时间：__BUILD_DATE__
- 提交：__COMMIT_HASH__
- 完整变更：[查看差异](__CHANGELOG_URL__)

### 📋 提交记录

__COMMIT_LOG__
