import json
from aivectormemory.config import USER_SCOPE_DIR
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.errors import success_response


def handle_digest(args, *, cm, session_id, **_):
    scope = args.get("scope", "project")
    since = args.get("since_sessions", 20)
    tags = args.get("tags")

    start_sid = max(1, session_id - since + 1)
    end_sid = session_id

    repo = MemoryRepo(cm.conn, cm.project_dir)
    pdir = USER_SCOPE_DIR if scope == "user" else cm.project_dir
    rows = repo.get_by_session_range(start_sid, end_sid, project_dir=pdir)

    memories = []
    for r in rows:
        if tags:
            mem_tags = json.loads(r.get("tags", "[]")) if isinstance(r.get("tags"), str) else r.get("tags", [])
            if not any(t in mem_tags for t in tags):
                continue
        memories.append({"id": r["id"], "content": r["content"], "tags": r["tags"], "created_at": r["created_at"]})

    return json.dumps(success_response(
        memories=memories, total_count=len(memories),
        session_range={"start": start_sid, "end": end_sid}
    ))
