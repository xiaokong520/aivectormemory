🌐 [简体中文](../README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | Español | [Deutsch](README.de.md) | [Français](README.fr.md) | [日本語](README.ja.md)

<p align="center">
  <h1 align="center">🧠 AIVectorMemory</h1>
  <p align="center">
    <strong>Dale memoria a tu asistente de IA — Servidor MCP de memoria persistente entre sesiones</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
    <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
  </p>
</p>

---

> **Problema**: Los asistentes de IA "olvidan" todo con cada nueva sesión — repitiendo los mismos errores, olvidando convenciones del proyecto, perdiendo el progreso de desarrollo. Peor aún, para compensar esta amnesia, tienes que inyectar contexto masivo en cada conversación, desperdiciando tokens.
>
> **AIVectorMemory**: Proporciona un almacén de memoria vectorial local para IA a través del protocolo MCP, permitiéndole recordar todo — conocimiento del proyecto, errores encontrados, decisiones de desarrollo, progreso de trabajo — persistente entre sesiones. La recuperación semántica bajo demanda elimina la inyección masiva, reduciendo drásticamente el consumo de tokens.

## ✨ Características Principales

| Característica | Descripción |
|----------------|-------------|
| 🔍 **Búsqueda Semántica** | Basada en similitud vectorial — buscar "timeout de base de datos" encuentra "error en pool de conexiones MySQL" |
| 🏠 **Completamente Local** | Inferencia local con ONNX Runtime, sin API Key, los datos nunca salen de tu máquina |
| 🔄 **Deduplicación Inteligente** | Similitud coseno > 0.95 actualiza automáticamente, sin almacenamiento duplicado |
| 📊 **Panel Web** | Interfaz de gestión integrada con visualización 3D de red vectorial |
| 🔌 **Todos los IDEs** | OpenCode / Claude Code / Cursor / Kiro / Windsurf / VSCode / Trae y más |
| 📁 **Aislamiento por Proyecto** | Una sola BD compartida entre proyectos, aislada automáticamente por project_dir |
| 🏷️ **Sistema de Etiquetas** | Categorización de memorias, búsqueda, renombrado y fusión de etiquetas |
| 💰 **Ahorro de Tokens** | Recuperación semántica bajo demanda reemplaza la inyección masiva de contexto, reduciendo 50%+ de tokens redundantes |
| 📋 **Seguimiento de Problemas** | Rastreador de issues ligero, IA registra y archiva automáticamente |

## 🏗️ Arquitectura

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
│  │     SQLite + sqlite-vec (Índice Vectorial) │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 Inicio Rápido

### Opción 1: Instalación con pip

```bash
pip install aivectormemory
cd /path/to/your/project
run install          # Selección interactiva de IDE, configuración con un clic
```

### Opción 2: uvx (sin instalación)

```bash
cd /path/to/your/project
uvx aivectormemory install
```

### Opción 3: Configuración manual

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
<summary>📍 Ubicación de archivos de configuración por IDE</summary>

| IDE | Ruta de configuración |
|-----|----------------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |

</details>

## 🛠️ 7 Herramientas MCP

### `remember` — Almacenar memoria

```
content (string, requerido)   Contenido en formato Markdown
tags    (string[], requerido)  Etiquetas, ej. ["error", "python"]
scope   (string)               "project" (por defecto) / "user" (entre proyectos)
```

Similitud > 0.95 actualiza automáticamente la memoria existente, sin duplicados.

### `recall` — Búsqueda semántica

```
query   (string)     Palabras clave de búsqueda semántica
tags    (string[])   Filtro exacto por etiquetas
scope   (string)     "project" / "user" / "all"
top_k   (integer)    Número de resultados, por defecto 5
```

Coincidencia por similitud vectorial — encuentra memorias relacionadas incluso con palabras diferentes.

### `forget` — Eliminar memorias

```
memory_id  (string)     ID individual
memory_ids (string[])   IDs en lote
```

### `status` — Estado de sesión

```
state (object, opcional)   Omitir para leer, pasar para actualizar
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

Mantiene el progreso de trabajo entre sesiones, restaura contexto automáticamente.

### `track` — Seguimiento de problemas

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   Título del problema
issue_id (integer)  ID del problema
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   Contenido de investigación
```

### `digest` — Resumen de memorias

```
scope          (string)    Alcance
since_sessions (integer)   Últimas N sesiones
tags           (string[])  Filtro por etiquetas
```

### `auto_save` — Guardado automático

```
decisions[]      Decisiones clave
modifications[]  Resúmenes de modificaciones de archivos
pitfalls[]       Registros de errores encontrados
todos[]          Elementos pendientes
```

Categoriza, etiqueta y deduplica automáticamente al final de cada conversación.

## 📊 Panel Web

```bash
run web --port 9080
```

Visita `http://localhost:9080` en tu navegador.

- Cambio entre múltiples proyectos, explorar/buscar/editar/eliminar memorias
- Estado de sesión, seguimiento de problemas
- Gestión de etiquetas (renombrar, fusionar, eliminación por lotes)
- Visualización 3D de red vectorial de memorias
- 🌐 Soporte multilingüe (简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語)

<p align="center">
  <img src="dashboard-projects.png" alt="Selección de Proyecto" width="100%">
  <br>
  <em>Selección de Proyecto</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="Resumen y Visualización de Red Vectorial" width="100%">
  <br>
  <em>Resumen y Visualización de Red Vectorial</em>
</p>

## ⚡ Combinación con Reglas Steering

AIVectorMemory es la capa de almacenamiento. Usa reglas Steering para indicar a la IA cuándo llamar:

```markdown
# Gestión de Memoria
- Nueva sesión: llamar status para leer estado
- Encontrar un error: llamar remember para registrar
- Buscar experiencia: llamar recall para buscar
- Fin de conversación: llamar auto_save para guardar
```

| IDE | Ubicación de Steering |
|-----|----------------------|
| Kiro | `.kiro/steering/*.md` |
| Cursor | `.cursor/rules/*.md` |
| Claude Code | `CLAUDE.md` |

## 🇨🇳 Usuarios en China

El modelo de Embedding (~200MB) se descarga automáticamente en la primera ejecución. Si es lento:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

O agregar env en la configuración MCP:

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Runtime | Python >= 3.10 |
| BD Vectorial | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| Tokenizador | HuggingFace Tokenizers |
| Protocolo | Model Context Protocol (MCP) |
| Web | HTTPServer nativo + Vanilla JS |

## License

MIT
