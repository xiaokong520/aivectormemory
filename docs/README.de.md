🌐 [简体中文](../README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [Español](README.es.md) | Deutsch | [Français](README.fr.md) | [日本語](README.ja.md)

<p align="center">
  <h1 align="center">🧠 AIVectorMemory</h1>
  <p align="center">
    <strong>Gib deinem KI-Programmierassistenten ein Gedächtnis — Sitzungsübergreifender persistenter Speicher MCP Server</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
    <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
  </p>
</p>

---

> **Problem**: KI-Assistenten „vergessen" alles bei jeder neuen Sitzung — sie wiederholen dieselben Fehler, vergessen Projektkonventionen und verlieren den Entwicklungsfortschritt. Schlimmer noch: Um diese Amnesie auszugleichen, muss man in jeder Konversation massiven Kontext injizieren und verschwendet dabei Tokens.
>
> **AIVectorMemory**: Stellt über das MCP-Protokoll einen lokalen Vektor-Speicher für KI bereit, der sich an alles erinnert — Projektwissen, Fehlerprotokolle, Entwicklungsentscheidungen, Arbeitsfortschritt — sitzungsübergreifend persistent. Semantischer Abruf bei Bedarf, keine Masseninjektion mehr, drastische Reduzierung des Token-Verbrauchs.

## ✨ Kernfunktionen

| Funktion | Beschreibung |
|----------|-------------|
| 🔍 **Semantische Suche** | Basierend auf Vektorähnlichkeit — Suche nach „Datenbank-Timeout" findet „MySQL Connection Pool Fehler" |
| 🏠 **Vollständig Lokal** | ONNX Runtime lokale Inferenz, kein API Key nötig, Daten verlassen nie deinen Rechner |
| 🔄 **Intelligente Deduplizierung** | Kosinus-Ähnlichkeit > 0.95 aktualisiert automatisch, keine doppelte Speicherung |
| 📊 **Web-Dashboard** | Integrierte Verwaltungsoberfläche mit 3D-Vektornetzwerk-Visualisierung |
| 🔌 **Alle IDEs** | OpenCode / Claude Code / Cursor / Kiro / Windsurf / VSCode / Trae und mehr |
| 📁 **Projektisolierung** | Eine gemeinsame DB für alle Projekte, automatisch isoliert durch project_dir |
| 🏷️ **Tag-System** | Erinnerungskategorisierung, Tag-Suche, Umbenennung, Zusammenführung |
| 💰 **Token Sparen** | Semantischer Abruf bei Bedarf ersetzt Massen-Kontextinjektion, 50%+ weniger redundante Tokens |
| 📋 **Problem-Tracking** | Leichtgewichtiger Issue-Tracker, KI zeichnet automatisch auf und archiviert |

## 🏗️ Architektur

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
│  │     SQLite + sqlite-vec (Vektorindex)      │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 Schnellstart

### Option 1: pip Installation

```bash
pip install aivectormemory
cd /path/to/your/project
run install          # Interaktive IDE-Auswahl, Ein-Klick-Konfiguration
```

### Option 2: uvx (ohne Installation)

```bash
cd /path/to/your/project
uvx aivectormemory install
```

### Option 3: Manuelle Konfiguration

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
<summary>📍 Konfigurationsdatei-Pfade nach IDE</summary>

| IDE | Konfigurationspfad |
|-----|-------------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |

</details>

## 🛠️ 7 MCP-Werkzeuge

### `remember` — Erinnerung speichern

```
content (string, erforderlich)   Inhalt im Markdown-Format
tags    (string[], erforderlich)  Tags, z.B. ["fehler", "python"]
scope   (string)                  "project" (Standard) / "user" (projektübergreifend)
```

Ähnlichkeit > 0.95 aktualisiert automatisch bestehende Erinnerung, keine Duplikate.

### `recall` — Semantische Suche

```
query   (string)     Semantische Suchbegriffe
tags    (string[])   Exakter Tag-Filter
scope   (string)     "project" / "user" / "all"
top_k   (integer)    Anzahl der Ergebnisse, Standard 5
```

Vektorähnlichkeits-Matching — findet verwandte Erinnerungen auch bei unterschiedlicher Wortwahl.

### `forget` — Erinnerungen löschen

```
memory_id  (string)     Einzelne ID
memory_ids (string[])   Mehrere IDs
```

### `status` — Sitzungsstatus

```
state (object, optional)   Weglassen zum Lesen, übergeben zum Aktualisieren
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

Hält den Arbeitsfortschritt sitzungsübergreifend, stellt Kontext automatisch wieder her.

### `track` — Problem-Tracking

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   Problemtitel
issue_id (integer)  Problem-ID
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   Untersuchungsinhalt
```

### `digest` — Erinnerungszusammenfassung

```
scope          (string)    Bereich
since_sessions (integer)   Letzte N Sitzungen
tags           (string[])  Tag-Filter
```

### `auto_save` — Automatisches Speichern

```
decisions[]      Wichtige Entscheidungen
modifications[]  Dateiänderungs-Zusammenfassungen
pitfalls[]       Fehlerprotokolle
todos[]          Offene Aufgaben
```

Kategorisiert, taggt und dedupliziert automatisch am Ende jeder Konversation.

## 📊 Web-Dashboard

```bash
run web --port 9080
```

Besuche `http://localhost:9080` im Browser.

- Mehrere Projekte wechseln, Erinnerungen durchsuchen/bearbeiten/löschen
- Sitzungsstatus, Problem-Tracking
- Tag-Verwaltung (Umbenennen, Zusammenführen, Stapellöschung)
- 3D-Vektornetzwerk-Visualisierung
- 🌐 Mehrsprachige Unterstützung (简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語)

<p align="center">
  <img src="dashboard-projects.png" alt="Projektauswahl" width="100%">
  <br>
  <em>Projektauswahl</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="Übersicht & Vektornetzwerk-Visualisierung" width="100%">
  <br>
  <em>Übersicht & Vektornetzwerk-Visualisierung</em>
</p>

## ⚡ Kombination mit Steering-Regeln

AIVectorMemory ist die Speicherschicht. Verwende Steering-Regeln, um der KI mitzuteilen, **wann und wie** sie diese Tools aufrufen soll.

`run install` generiert automatisch Steering-Regeln und Hooks-Konfiguration — kein manuelles Setup nötig.

| IDE | Steering-Pfad | Hooks |
|-----|--------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | — |
| Claude Code | `CLAUDE.md` (angehängt) | — |
| Windsurf | `.windsurf/rules/aivectormemory.md` | — |
| VSCode | `.github/copilot-instructions.md` (angehängt) | — |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md` (angehängt) | — |

<details>
<summary>📋 Steering-Regeln Beispiel (automatisch generiert)</summary>

```markdown
# AIVectorMemory - Sitzungsübergreifender persistenter Speicher

## Startprüfung

Zu Beginn jeder neuen Sitzung in dieser Reihenfolge ausführen:

1. `status` aufrufen (ohne Parameter) um Sitzungsstatus zu lesen, `is_blocked` und `block_reason` prüfen
2. `recall` aufrufen (tags: ["Projektwissen"], scope: "project") um Projektwissen zu laden
3. `recall` aufrufen (tags: ["preference"], scope: "user") um Benutzereinstellungen zu laden

## Wann aufrufen

- Neue Sitzung beginnt: `status` aufrufen um vorherigen Arbeitsstatus zu lesen
- Fehler gefunden: `remember` aufrufen um zu protokollieren, Tag "Fehler" hinzufügen
- Historische Erfahrung benötigt: `recall` für semantische Suche aufrufen
- Bug oder TODO gefunden: `track` (action: create) aufrufen
- Aufgabenfortschritt ändert sich: `status` (state Parameter übergeben) zum Aktualisieren
- Vor Konversationsende: `auto_save` aufrufen um diese Sitzung zu speichern

## Sitzungsstatus-Verwaltung

status-Felder: is_blocked, block_reason, current_task, next_step,
progress[], recent_changes[], pending[]

## Problemverfolgung

1. `track create` → Problem erfassen
2. `track update` → Untersuchungsinhalt aktualisieren
3. `track archive` → Gelöste Probleme archivieren
```

</details>

<details>
<summary>🔗 Hooks-Konfiguration Beispiel (nur Kiro, automatisch generiert)</summary>

Automatisches Speichern bei Sitzungsende (`.kiro/hooks/auto-save-session.kiro.hook`):

```json
{
  "enabled": true,
  "name": "Sitzung automatisch speichern",
  "version": "1",
  "when": { "type": "agentStop" },
  "then": {
    "type": "askAgent",
    "prompt": "auto_save aufrufen um Entscheidungen, Änderungen, Fehler und Aufgaben dieser Sitzung kategorisiert zu speichern"
  }
}
```

Entwicklungsworkflow-Prüfung (`.kiro/hooks/dev-workflow-check.kiro.hook`):

```json
{
  "enabled": true,
  "name": "Entwicklungsworkflow-Prüfung",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "Kernprinzipien: Vor dem Handeln verifizieren, kein blindes Testen, erst nach bestandenen Tests als erledigt markieren"
  }
}
```

</details>

## 🇨🇳 Nutzer in China

Das Embedding-Modell (~200MB) wird beim ersten Start automatisch heruntergeladen. Falls langsam:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

Oder env in der MCP-Konfiguration hinzufügen:

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 Technologie-Stack

| Komponente | Technologie |
|------------|-----------|
| Laufzeit | Python >= 3.10 |
| Vektor-DB | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| Tokenizer | HuggingFace Tokenizers |
| Protokoll | Model Context Protocol (MCP) |
| Web | Nativer HTTPServer + Vanilla JS |

## License

MIT
