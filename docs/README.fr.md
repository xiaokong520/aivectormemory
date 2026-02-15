🌐 [简体中文](../README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [Español](README.es.md) | [Deutsch](README.de.md) | Français | [日本語](README.ja.md)

<p align="center">
  <h1 align="center">🧠 AIVectorMemory</h1>
  <p align="center">
    <strong>Donnez une mémoire à votre assistant IA — Serveur MCP de mémoire persistante inter-sessions</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
    <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
  </p>
</p>

---

> **Problème** : Les assistants IA « oublient » tout à chaque nouvelle session — répétant les mêmes erreurs, oubliant les conventions du projet, perdant la progression du développement. Pire encore, pour compenser cette amnésie, vous devez injecter un contexte massif dans chaque conversation, gaspillant des tokens.
>
> **AIVectorMemory** : Fournit un stockage de mémoire vectorielle local pour l'IA via le protocole MCP, lui permettant de se souvenir de tout — connaissances du projet, erreurs rencontrées, décisions de développement, progression du travail — persistant entre les sessions. La récupération sémantique à la demande élimine l'injection massive, réduisant considérablement la consommation de tokens.

## ✨ Fonctionnalités Principales

| Fonctionnalité | Description |
|----------------|-------------|
| 🔍 **Recherche Sémantique** | Basée sur la similarité vectorielle — chercher « timeout base de données » trouve « erreur pool de connexions MySQL » |
| 🏠 **Entièrement Local** | Inférence locale ONNX Runtime, pas de clé API nécessaire, les données ne quittent jamais votre machine |
| 🔄 **Déduplication Intelligente** | Similarité cosinus > 0.95 met à jour automatiquement, pas de stockage en double |
| 📊 **Tableau de Bord Web** | Interface de gestion intégrée avec visualisation 3D du réseau vectoriel |
| 🔌 **Tous les IDEs** | OpenCode / Claude Code / Cursor / Kiro / Windsurf / VSCode / Trae et plus |
| 📁 **Isolation par Projet** | Une seule BD partagée entre projets, isolée automatiquement par project_dir |
| 🏷️ **Système d'Étiquettes** | Catégorisation des mémoires, recherche, renommage et fusion d'étiquettes |
| 💰 **Économie de Tokens** | Récupération sémantique à la demande remplace l'injection massive de contexte, réduisant 50%+ de tokens redondants |
| 📋 **Suivi des Problèmes** | Traqueur d'issues léger, l'IA enregistre et archive automatiquement |

## 🏗️ Architecture

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
│  │     SQLite + sqlite-vec (Index Vectoriel)  │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 Démarrage Rapide

### Option 1 : Installation pip

```bash
pip install aivectormemory
cd /path/to/your/project
run install          # Sélection interactive de l'IDE, configuration en un clic
```

### Option 2 : uvx (sans installation)

```bash
cd /path/to/your/project
uvx aivectormemory install
```

### Option 3 : Configuration manuelle

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
<summary>📍 Emplacements des fichiers de configuration par IDE</summary>

| IDE | Chemin de configuration |
|-----|------------------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |

</details>

## 🛠️ 7 Outils MCP

### `remember` — Stocker une mémoire

```
content (string, requis)   Contenu au format Markdown
tags    (string[], requis)  Étiquettes, ex. ["erreur", "python"]
scope   (string)            "project" (par défaut) / "user" (inter-projets)
```

Similarité > 0.95 met à jour automatiquement la mémoire existante, sans doublons.

### `recall` — Recherche sémantique

```
query   (string)     Mots-clés de recherche sémantique
tags    (string[])   Filtre exact par étiquettes
scope   (string)     "project" / "user" / "all"
top_k   (integer)    Nombre de résultats, par défaut 5
```

Correspondance par similarité vectorielle — trouve des mémoires liées même avec des mots différents.

### `forget` — Supprimer des mémoires

```
memory_id  (string)     ID unique
memory_ids (string[])   IDs en lot
```

### `status` — État de session

```
state (object, optionnel)   Omettre pour lire, passer pour mettre à jour
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

Maintient la progression du travail entre les sessions, restaure automatiquement le contexte.

### `track` — Suivi des problèmes

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   Titre du problème
issue_id (integer)  ID du problème
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   Contenu d'investigation
```

### `digest` — Résumé des mémoires

```
scope          (string)    Portée
since_sessions (integer)   N dernières sessions
tags           (string[])  Filtre par étiquettes
```

### `auto_save` — Sauvegarde automatique

```
decisions[]      Décisions clés
modifications[]  Résumés des modifications de fichiers
pitfalls[]       Registres d'erreurs rencontrées
todos[]          Éléments en attente
```

Catégorise, étiquette et déduplique automatiquement à la fin de chaque conversation.

## 📊 Tableau de Bord Web

```bash
run web --port 9080
```

Visitez `http://localhost:9080` dans votre navigateur.

- Basculement entre projets, parcourir/rechercher/modifier/supprimer les mémoires
- État de session, suivi des problèmes
- Gestion des étiquettes (renommer, fusionner, suppression par lots)
- Visualisation 3D du réseau vectoriel de mémoires
- 🌐 Support multilingue (简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語)

<p align="center">
  <img src="dashboard-projects.png" alt="Sélection de Projet" width="100%">
  <br>
  <em>Sélection de Projet</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="Aperçu & Visualisation du Réseau Vectoriel" width="100%">
  <br>
  <em>Aperçu & Visualisation du Réseau Vectoriel</em>
</p>

## ⚡ Combinaison avec les Règles Steering

AIVectorMemory est la couche de stockage. Utilisez les règles Steering pour indiquer à l'IA **quand et comment** appeler ces outils.

L'exécution de `run install` génère automatiquement les règles Steering et la configuration des Hooks — aucune configuration manuelle nécessaire.

| IDE | Emplacement Steering | Hooks |
|-----|---------------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | — |
| Claude Code | `CLAUDE.md` (ajouté) | — |
| Windsurf | `.windsurf/rules/aivectormemory.md` | — |
| VSCode | `.github/copilot-instructions.md` (ajouté) | — |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md` (ajouté) | — |

<details>
<summary>📋 Exemple de Règles Steering (généré automatiquement)</summary>

```markdown
# AIVectorMemory - Mémoire Persistante Inter-Sessions

## Vérification au Démarrage

Au début de chaque nouvelle session, exécuter dans l'ordre :

1. Appeler `status` (sans paramètres) pour lire l'état de la session, vérifier `is_blocked` et `block_reason`
2. Appeler `recall` (tags: ["connaissance-projet"], scope: "project") pour charger les connaissances du projet
3. Appeler `recall` (tags: ["preference"], scope: "user") pour charger les préférences utilisateur

## Quand Appeler

- Nouvelle session : appeler `status` pour lire l'état de travail précédent
- Erreur trouvée : appeler `remember` pour enregistrer, ajouter le tag "erreur"
- Besoin d'expérience historique : appeler `recall` pour recherche sémantique
- Bug ou tâche trouvé : appeler `track` (action: create)
- Changement de progression : appeler `status` (passer le paramètre state) pour mettre à jour
- Avant la fin de la conversation : appeler `auto_save` pour sauvegarder cette session

## Gestion de l'État de Session

Champs status : is_blocked, block_reason, current_task, next_step,
progress[], recent_changes[], pending[]

## Suivi des Problèmes

1. `track create` → Enregistrer le problème
2. `track update` → Mettre à jour le contenu d'investigation
3. `track archive` → Archiver les problèmes résolus
```

</details>

<details>
<summary>🔗 Exemple de Configuration Hooks (Kiro uniquement, généré automatiquement)</summary>

Sauvegarde automatique en fin de session (`.kiro/hooks/auto-save-session.kiro.hook`) :

```json
{
  "enabled": true,
  "name": "Sauvegarde Automatique de Session",
  "version": "1",
  "when": { "type": "agentStop" },
  "then": {
    "type": "askAgent",
    "prompt": "Appeler auto_save pour catégoriser et sauvegarder les décisions, modifications, erreurs et tâches en attente"
  }
}
```

Vérification du workflow de développement (`.kiro/hooks/dev-workflow-check.kiro.hook`) :

```json
{
  "enabled": true,
  "name": "Vérification du Workflow de Développement",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "Principes : vérifier avant d'agir, pas de tests à l'aveugle, ne marquer comme terminé qu'après réussite des tests"
  }
}
```

</details>

## 🇨🇳 Utilisateurs en Chine

Le modèle d'Embedding (~200Mo) est téléchargé automatiquement au premier lancement. Si c'est lent :

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

Ou ajouter env dans la configuration MCP :

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 Stack Technique

| Composant | Technologie |
|-----------|-----------|
| Runtime | Python >= 3.10 |
| BD Vectorielle | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| Tokenizer | HuggingFace Tokenizers |
| Protocole | Model Context Protocol (MCP) |
| Web | HTTPServer natif + Vanilla JS |

## License

MIT
