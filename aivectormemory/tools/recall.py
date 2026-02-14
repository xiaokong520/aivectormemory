import json
from aivectormemory.config import DEFAULT_TOP_K
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.errors import success_response


def handle_recall(args, *, cm, engine, **_):
    query = args.get("query")
    scope = args.get("scope", "all")
    tags = args.get("tags")
    top_k = args.get("top_k", DEFAULT_TOP_K)

    repo = MemoryRepo(cm.conn, cm.project_dir)

    if not query:
        if not tags:
            raise ValueError("query or tags is required")
        rows = repo.list_by_tags(tags, scope=scope, project_dir=cm.project_dir, limit=top_k)
        for r in rows:
            r["similarity"] = 1.0
        return json.dumps(success_response(memories=rows))

    embedding = engine.encode(query)
    rows = repo.search_by_vector(embedding, top_k=top_k, scope=scope, project_dir=cm.project_dir)

    results = []
    for r in rows:
        distance = r.pop("distance", 0)
        r["similarity"] = round(1 - (distance ** 2) / 2, 4)
        if tags:
            mem_tags = json.loads(r.get("tags", "[]")) if isinstance(r.get("tags"), str) else r.get("tags", [])
            if not any(t in mem_tags for t in tags):
                continue
        results.append(r)

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return json.dumps(success_response(memories=results[:top_k]))
