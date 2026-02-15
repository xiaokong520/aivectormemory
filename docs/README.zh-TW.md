🌐 [简体中文](../README.md) | 繁體中文 | [English](README.en.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [日本語](README.ja.md)

<p align="center">
  <h1 align="center">🧠 AIVectorMemory</h1>
  <p align="center">
    <strong>為 AI 程式助手裝上記憶 — 跨會話持久化記憶 MCP Server</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
    <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
  </p>
</p>

---

> **問題**：AI 助手每次新會話都「失憶」，反覆踩同樣的坑、忘記專案約定、遺失開發進度。更糟的是，為了補償失憶，你不得不在每次對話中重複注入大量上下文，白白浪費 Token。
>
> **AIVectorMemory**：透過 MCP 協議為 AI 提供本地向量記憶庫，讓它記住一切 — 專案知識、踩坑記錄、開發決策、工作進度 — 跨會話永不遺失。語義檢索按需召回，不再全量注入，大幅降低 Token 消耗。

## ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🔍 **語義搜尋** | 基於向量相似度，搜「資料庫逾時」能找到「MySQL 連線池踩坑」 |
| 🏠 **完全本地** | ONNX Runtime 本地推理，無需 API Key，資料不出本機 |
| 🔄 **智慧去重** | 餘弦相似度 > 0.95 自動更新，不會重複儲存 |
| 📊 **Web 看板** | 內建管理介面，3D 向量網路視覺化 |
| 🔌 **全 IDE 支援** | OpenCode / Claude Code / Cursor / Kiro / Windsurf / VSCode / Trae 等 |
| 📁 **專案隔離** | 多專案共用一個 DB，透過 project_dir 自動隔離 |
| 🏷️ **標籤體系** | 記憶分類管理，支援標籤搜尋、重新命名、合併 |
| 💰 **節省 Token** | 語義檢索按需召回，替代全量上下文注入，減少 50%+ 重複 Token 消耗 |
| 📋 **問題追蹤** | 輕量級 issue tracker，AI 自動記錄和歸檔 |

## 🏗️ 架構

```
┌─────────────────────────────────────────────────┐
│                   AI IDE                         │
│  OpenCode / Claude Code / Cursor / Kiro / ...   │
└──────────────────────┬──────────────────────────┘
                       │ MCP Protocol (stdio)
┌──────────────────────▼──────────────────────────┐
│              AIVectorMemory Server               │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ remember │ │  recall   │ │   auto_save      │ │
│  │ forget   │ │  digest   │ │   status/track   │ │
│  └────┬─────┘ └────┬─────┘ └───────┬──────────┘ │
│       │            │               │             │
│  ┌────▼────────────▼───────────────▼──────────┐  │
│  │         Embedding Engine (ONNX)            │  │
│  │      intfloat/multilingual-e5-small        │  │
│  └────────────────────┬───────────────────────┘  │
│                       │                          │
│  ┌────────────────────▼───────────────────────┐  │
│  │     SQLite + sqlite-vec（向量索引）         │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 快速開始

### 方式一：pip 安裝

```bash
pip install aivectormemory
cd /path/to/your/project
run install          # 互動式選擇 IDE，一鍵配置
```

### 方式二：uvx 執行（零安裝）

```bash
cd /path/to/your/project
uvx aivectormemory install
```

### 方式三：手動配置

```json
{
  "mcpServers": {
    "aivectormemory": {
      "command": "run",
      "args": ["--project-dir", "/path/to/your/project"]
    }
  }
}
```

<details>
<summary>📍 各 IDE 設定檔位置</summary>

| IDE | 設定檔路徑 |
|-----|------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |

</details>

## 🛠️ 7 個 MCP 工具

### `remember` — 存入記憶

```
content (string, 必填)   記憶內容，Markdown 格式
tags    (string[], 必填)  標籤，如 ["踩坑", "python"]
scope   (string)          "project"（預設）/ "user"（跨專案）
```

相似度 > 0.95 自動更新已有記憶，不重複儲存。

### `recall` — 語義搜尋

```
query   (string)     語義搜尋關鍵詞
tags    (string[])   標籤精確過濾
scope   (string)     "project" / "user" / "all"
top_k   (integer)    回傳數量，預設 5
```

向量相似度匹配，用詞不同也能找到相關記憶。

### `forget` — 刪除記憶

```
memory_id  (string)     單個 ID
memory_ids (string[])   批次 ID
```

### `status` — 會話狀態

```
state (object, 可選)   不傳=讀取，傳=更新
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

跨會話保持工作進度，新會話自動恢復上下文。

### `track` — 問題追蹤

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   問題標題
issue_id (integer)  問題 ID
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   排查內容
```

### `digest` — 記憶摘要

```
scope          (string)    範圍
since_sessions (integer)   最近 N 次會話
tags           (string[])  標籤過濾
```

### `auto_save` — 自動儲存

```
decisions[]      關鍵決策
modifications[]  檔案修改摘要
pitfalls[]       踩坑記錄
todos[]          待辦事項
```

每次對話結束自動分類儲存，打標籤，去重。

## 📊 Web 看板

```bash
run web --port 9080
```

瀏覽器存取 `http://localhost:9080`

- 多專案切換，記憶瀏覽/搜尋/編輯/刪除
- 會話狀態、問題追蹤
- 標籤管理（重新命名、合併、批次刪除）
- 3D 向量記憶網路視覺化
- 🌐 多語言支援（简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語）

<p align="center">
  <img src="dashboard-projects.png" alt="專案選擇" width="100%">
  <br>
  <em>專案選擇</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="統計概覽 & 向量網路視覺化" width="100%">
  <br>
  <em>統計概覽 & 向量網路視覺化</em>
</p>

## ⚡ 搭配 Steering 規則

AIVectorMemory 是儲存層，透過 Steering 規則告訴 AI 何時呼叫：

```markdown
# 記憶管理
- 新會話開始：呼叫 status 讀取狀態
- 遇到踩坑：呼叫 remember 記錄
- 查找經驗：呼叫 recall 搜尋
- 對話結束：呼叫 auto_save 儲存
```

| IDE | Steering 位置 |
|-----|--------------|
| Kiro | `.kiro/steering/*.md` |
| Cursor | `.cursor/rules/*.md` |
| Claude Code | `CLAUDE.md` |

## 🇨🇳 中國大陸使用者

首次執行自動下載 Embedding 模型（~200MB），如果慢：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

或在 MCP 設定中加 env：

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 技術棧

| 元件 | 技術 |
|------|------|
| 執行環境 | Python >= 3.10 |
| 向量資料庫 | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| 分詞器 | HuggingFace Tokenizers |
| 協議 | Model Context Protocol (MCP) |
| Web | 原生 HTTPServer + Vanilla JS |

## License

MIT
