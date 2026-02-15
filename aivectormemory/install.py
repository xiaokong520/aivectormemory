"""aivectormemory install - 交互式为当前项目配置 MCP + Steering 规则"""
import json
import platform
from pathlib import Path

# (IDE名, MCP配置路径, MCP格式, 是否全局, Steering路径, Steering写入方式, Hooks目录)
# steering_mode: "file"=独立文件 "append"=追加到已有文件 None=不写Steering
# hooks_dir: lambda返回hooks目录路径, None=不支持hooks
IDES = [
    ("Kiro",           lambda root: root / ".kiro/settings/mcp.json",  "standard", False,
     lambda root: root / ".kiro/steering/aivectormemory.md", "file",
     lambda root: root / ".kiro/hooks"),
    ("Cursor",         lambda root: root / ".cursor/mcp.json",         "standard", False,
     lambda root: root / ".cursor/rules/aivectormemory.md", "file", None),
    ("Claude Code",    lambda root: root / ".mcp.json",                "standard", False,
     lambda root: root / "CLAUDE.md", "append", None),
    ("Windsurf",       lambda root: root / ".windsurf/mcp.json",       "standard", False,
     lambda root: root / ".windsurf/rules/aivectormemory.md", "file", None),
    ("VSCode",         lambda root: root / ".vscode/mcp.json",         "standard", False,
     lambda root: root / ".github/copilot-instructions.md", "append", None),
    ("Trae",           lambda root: root / ".trae/mcp.json",           "standard", False,
     lambda root: root / ".trae/rules/aivectormemory.md", "file", None),
    ("OpenCode",       lambda root: root / "opencode.json",            "opencode", False,
     lambda root: root / "AGENTS.md", "append", None),
    ("Claude Desktop", lambda _: _claude_desktop_path(),               "standard", True,
     None, None, None),
]

RUNNERS = [
    ("run（pip/pipx 安装）", lambda pdir: ("run", ["--project-dir", pdir])),
    ("uvx aivectormemory（无需安装）", lambda pdir: ("uvx", ["aivectormemory@latest", "--project-dir", pdir])),
]


STEERING_MARKER = "<!-- aivectormemory-steering -->"

STEERING_CONTENT = """# AIVectorMemory - 跨会话持久记忆

本项目已配置 AIVectorMemory MCP Server，提供以下 7 个工具。请在合适的时机主动调用。

## 启动检查

每次新会话开始时，按以下顺序执行：

1. 调用 `status`（不传参数）读取会话状态，检查 `is_blocked` 和 `block_reason`
2. 调用 `recall`（tags: ["项目知识"], scope: "project", top_k: 100）加载项目知识
3. 调用 `recall`（tags: ["preference"], scope: "user", top_k: 20）加载用户偏好

⚠️ 阻塞状态优先级最高：有阻塞 → 等用户反馈，禁止执行任何操作

## 何时调用

- 新会话开始时：调用 `status`（不传参数）读取上次的工作状态，了解进度和阻塞情况
- 遇到踩坑/技术要点时：调用 `remember` 记录，标签加 "踩坑"
- 需要查找历史经验时：调用 `recall` 语义搜索，或按标签精确查询
- 发现 bug 或待处理事项时：调用 `track`（action: create）记录问题
- 修复问题后：调用 `track`（action: update）更新排查内容和结论
- 问题关闭时：调用 `track`（action: archive）归档
- 任务进度变化时：调用 `status`（传 state 参数）更新当前任务、进度、最近修改
- 对话结束前：调用 `auto_save` 保存本次对话的决策、修改、踩坑、待办、偏好

## 工具速查

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| remember | 存入记忆 | content, tags, scope(project/user) |
| recall | 语义搜索记忆 | query, tags, scope, top_k |
| forget | 删除记忆 | memory_id / memory_ids |
| status | 会话状态管理 | state(不传=读取, 传=更新) |
| track | 问题跟踪 | action(create/update/archive/list) |
| digest | 记忆摘要 | scope, since_sessions, tags |
| auto_save | 自动保存会话 | decisions, modifications, pitfalls, todos, preferences |

## 会话状态管理

status 字段说明：
- `is_blocked`：是否阻塞
- `block_reason`：阻塞原因
- `current_task`：当前任务
- `next_step`：下一步（只能由用户确认后填写，禁止擅自填写）
- `progress`：进度列表
- `recent_changes`：最近修改（不超过10条）
- `pending`：待处理事项

何时设置阻塞（is_blocked: true）：修复完成等用户验证、方案待用户确认、需要用户决策
何时清除阻塞（is_blocked: false）：用户确认验证通过、用户确认方案、用户做出决策

更新时机：任务开始、完成子任务、遇到问题转向、任务完成

## 知识库管理

- 遇到问题必记：命令失败、框架踩坑、技术要点 → `remember`（标签：踩坑）
- 查询踩坑记录：`recall`（query: 关键词, tags: ["踩坑"]）
- 禁止猜测用户意图，必须有用户明确表态才能记录

## 问题追踪

问题处理原则：
- 一次只修一个问题
- 修复过程中发现新问题 → `track create` 记录标题后继续当前问题
- 当前问题修复完成后，再按顺序处理新问题

问题记录流程：
1. `track create`：记录问题标题，`status` 更新 pending
2. 排查问题原因，`track update` 更新 content（根因、方案）
3. 向用户说明问题和方案
4. 修改代码并自测
5. 自测通过后 `track update` 更新结论，等用户验证
6. 用户确认没问题 → `track archive` 归档

## 核心原则

1. 任何操作前必须验证，不能假设，不能靠记忆
2. 遇到问题禁止盲目测试，必须找到根本原因
3. 禁止口头承诺，一切以测试通过为准
4. 任何文件修改前必须查看代码严谨思考
5. 开发、自测过程中禁止让用户手动操作，能自己执行的不要让用户做

## 自测要求

- 代码修改后必须自测验证
- 自测通过后才能说"等待验证"
- 禁止模糊表述："基本完成"、"差不多"、"应该是"等词汇禁止使用
- 任务只有两种状态：完成 或 未完成

## auto_save 规范

对话结束前调用 `auto_save`，分类保存：
- decisions：本次对话的关键决策
- modifications：修改的文件和内容摘要（每个文件一条）
- pitfalls：遇到的坑和解决方案
- todos：产生的待办事项
- preferences：用户表达的技术偏好（scope 固定 user，跨项目通用）

规则：每条内容必须具体可追溯，没有的分类传空数组，不要编造

## 代码风格

简洁优先：
- 能用三目运算符，不用 if-else
- 能用短路求值，不用条件判断
- 能用解构赋值，不用逐个取值
- 能用模板字符串，不用字符串拼接

避免冗余：
- 不写无意义的注释
- 不写重复的代码，提取公共函数
- 变量命名清晰，不需要注释解释

## 完成标准

禁止模糊表述：
- 禁止"基本完成"、"差不多"、"大致实现"等词汇
- 任务只有两种状态：完成 或 未完成

完成确认流程：
1. 逐项检查：对照任务清单逐一验证
2. 代码验证：确认代码存在且正确
3. 功能测试：编译或运行测试验证
4. 标记完成：测试通过后才标记完成

## 错误处理

反复失败时：
1. 记录已尝试的方法
2. 换一种思路解决
3. 仍然失败则询问用户

遇到报错或异常时：
- 禁止盲目测试，必须分析问题根本原因
- 必须查看问题对应的代码文件
- 修复方案必须与实际错误对应

## 自检要求

完成任务前必须自问：
1. 排查是否完整？
2. 数据是否准确？
3. 逻辑是否严谨？

禁止：
- 禁止说"大部分"、"基本上"、"应该是"等模糊词
- 禁止未经验证就下结论

## 代码修改检查

修改前：
- 调用 `recall` 查询相关踩坑记录
- 必须先查看该功能的现有实现
- 涉及数据存储时，必须确认数据流向

修改后：
- 运行相关测试或编译验证
- 确认修改不影响其他功能
"""


HOOKS_CONFIGS = [
    {
        "filename": "auto-save-session.kiro.hook",
        "content": {
            "enabled": True,
            "name": "会话结束自动保存",
            "description": "每次 agent 执行结束时，自动调用 mcp_aivectormemory_auto_save 保存本次对话的决策、修改、踩坑、待办",
            "version": "1",
            "when": {"type": "agentStop"},
            "then": {
                "type": "askAgent",
                "prompt": (
                    "【会话结束自动保存】请立即调用 mcp_aivectormemory_auto_save，将本次对话的关键信息分类保存：\n\n"
                    "1. decisions：本次对话做出的关键决策（技术方案选择、架构决定等）\n"
                    "2. modifications：本次对话修改的文件和内容摘要（每个文件一条）\n"
                    "3. pitfalls：本次对话遇到的坑和解决方案\n"
                    "4. todos：本次对话产生的待办事项\n"
                    "5. preferences：用户表达的技术偏好、设计风格倾向、架构选择习惯\n\n"
                    "规则：\n"
                    "- 每条内容必须具体、可追溯，禁止模糊描述\n"
                    "- 没有的分类传空数组，不要编造\n"
                    "- scope 默认 project（preferences 固定 user，跨项目通用）"
                ),
            },
            "shortName": "auto-save-session",
        },
    },
    {
        "filename": "dev-workflow-check.kiro.hook",
        "content": {
            "enabled": True,
            "name": "开发流程检查",
            "description": "每次收到用户消息时，检查核心原则、问题处理原则、自测要求",
            "version": "1",
            "when": {"type": "promptSubmit"},
            "then": {
                "type": "askAgent",
                "prompt": (
                    "## ⚠️ 核心原则\n\n"
                    "1. 任何操作前必须验证，不能假设，不能靠记忆\n"
                    "2. 遇到问题禁止盲目测试，必须查看代码找到根本原因\n"
                    "3. 禁止口头承诺，一切以测试通过为准\n"
                    "4. 任何文件修改前必须查看代码严谨思考\n"
                    "5. 开发、自测过程中禁止让用户手动操作\n\n"
                    "## ⚠️ 自测要求\n\n"
                    "禁止让用户手动操作 - 能自己执行的，不要让用户做\n\n"
                    "- Python：python -m pytest 或直接运行脚本验证\n"
                    "- MCP Server：通过 stdio 发送 JSON-RPC 消息验证\n"
                    "- Web 看板：Playwright 验证\n"
                    "- 自测通过后才能说\"等待验证\""
                ),
            },
            "shortName": "dev-workflow-check",
        },
    },
]


def _write_hooks(hooks_dir: Path) -> list[str]:
    """写入 hook 文件到指定目录，返回变更列表"""
    results = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    for hook in HOOKS_CONFIGS:
        filepath = hooks_dir / hook["filename"]
        new_content = json.dumps(hook["content"], indent=2, ensure_ascii=False) + "\n"
        if filepath.exists():
            existing = filepath.read_text("utf-8")
            if existing.strip() == new_content.strip():
                results.append(f"- 无变更  Hook: {hook['filename']}")
                continue
        filepath.write_text(new_content, encoding="utf-8")
        results.append(f"✓ 已生成  Hook: {hook['filename']}")
    return results


def _write_steering(filepath: Path, mode: str) -> bool:
    if mode == "file":
        content = STEERING_CONTENT.strip() + "\n"
        if filepath.exists() and filepath.read_text("utf-8").strip() == content.strip():
            return False
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        return True
    if mode == "append":
        existing = filepath.read_text("utf-8") if filepath.exists() else ""
        block = f"\n{STEERING_MARKER}\n{STEERING_CONTENT.strip()}\n"
        if STEERING_MARKER in existing:
            start = existing.index(STEERING_MARKER)
            next_marker = existing.find("\n<!-- ", start + len(STEERING_MARKER))
            end = next_marker if next_marker != -1 else len(existing)
            old_block = existing[start:end]
            new_block = f"{STEERING_MARKER}\n{STEERING_CONTENT.strip()}\n"
            if old_block.strip() == new_block.strip():
                return False
            updated = existing[:start] + new_block + existing[end:]
            filepath.write_text(updated, encoding="utf-8")
            return True
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(block)
        return True
    return False


def _claude_desktop_path() -> Path | None:
    s = platform.system()
    if s == "Darwin":
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    if s == "Windows":
        import os
        return Path(os.environ.get("APPDATA", "")) / "Claude/claude_desktop_config.json"
    if s == "Linux":
        return Path.home() / ".config/Claude/claude_desktop_config.json"
    return None


def _build_config(cmd: str, args: list[str], fmt: str) -> dict:
    if fmt == "opencode":
        return {"type": "local", "command": [cmd] + args, "enabled": True}
    return {"command": cmd, "args": args}


def _merge_config(filepath: Path, key: str, server_name: str, server_config: dict) -> bool:
    config = {}
    if filepath.exists():
        try:
            config = json.loads(filepath.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            config = {}
    config.setdefault(key, {})
    if server_name in config[key] and config[key][server_name] == server_config:
        return False
    config[key][server_name] = server_config
    old_key = "aivectormemory"
    if old_key in config[key] and old_key != server_name:
        del config[key][old_key]
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def _choose(prompt: str, options: list[tuple], allow_all: bool = False) -> list | None:
    for i, (label, *_) in enumerate(options, 1):
        print(f"  {i}. {label}")
    if allow_all:
        print(f"  a. 全部安装")
    print()
    choice = input(f"{prompt}: ").strip().lower()
    if not choice:
        return None
    if allow_all and choice == "a":
        return list(range(len(options)))
    nums = {int(p.strip()) - 1 for p in choice.split(",") if p.strip().isdigit()}
    selected = [i for i in nums if 0 <= i < len(options)]
    return selected or None


def run_install(project_dir: str | None = None):
    pdir = str(Path(project_dir or ".").resolve()).replace("\\", "/")
    print(f"项目目录: {pdir}\n")

    # 1. 选择启动方式
    print("启动方式：")
    runner_indices = _choose("选择启动方式 [1]", RUNNERS)
    if runner_indices is None:
        runner_indices = [0]  # 默认 pip/pipx
    cmd, args = RUNNERS[runner_indices[0]][1](pdir)
    print(f"  → {cmd} {' '.join(args)}\n")

    # 2. 选择 IDE
    print("支持的 IDE：")
    valid_ides = []
    for name, path_fn, fmt, is_global, steering_fn, steering_mode, hooks_fn in IDES:
        p = path_fn(Path(pdir))
        if p is None:
            continue
        tag = " (全局)" if is_global else ""
        valid_ides.append((f"{name}{tag}", path_fn, fmt, steering_fn, steering_mode, hooks_fn))

    ide_indices = _choose("选择 IDE（编号，逗号分隔多选，a=全部）", valid_ides, allow_all=True)
    if ide_indices is None:
        print("未选择，退出")
        return

    # 3. 写入配置
    print()
    root = Path(pdir)
    for idx in ide_indices:
        label, path_fn, fmt, steering_fn, steering_mode, hooks_fn = valid_ides[idx]
        filepath = path_fn(root)
        if filepath is None:
            continue
        server_config = _build_config(cmd, args, fmt)
        key = "mcp" if fmt == "opencode" else "mcpServers"
        changed = _merge_config(filepath, key, "aivectormemory", server_config)
        status = "✓ 已更新" if changed else "- 无变更"
        print(f"  {status}  {label} MCP 配置")

        # 4. 写入 Steering 规则
        if steering_fn and steering_mode:
            steering_path = steering_fn(root)
            s_changed = _write_steering(steering_path, steering_mode)
            s_status = "✓ 已生成" if s_changed else "- 无变更"
            print(f"  {s_status}  {label} Steering 规则 → {steering_path.relative_to(root)}")

        # 5. 写入 Hooks
        if hooks_fn:
            hooks_dir = hooks_fn(root)
            hook_results = _write_hooks(hooks_dir)
            for r in hook_results:
                print(f"  {r}")

    print("\n安装完成，重启 IDE 即可使用")
