import json
import sqlite3
import uuid
from datetime import datetime, timezone
from aivectormemory.config import USER_SCOPE_DIR


class MemoryRepo:
    def __init__(self, conn: sqlite3.Connection, project_dir: str = ""):
        self.conn = conn
        self.project_dir = project_dir

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def insert(self, content: str, tags: list[str], scope: str, session_id: int,
               embedding: list[float], dedup_threshold: float = 0.95) -> dict:
        pdir = USER_SCOPE_DIR if scope == "user" else self.project_dir
        dup = self.find_duplicate(embedding, dedup_threshold, pdir)
        if dup:
            return self.update(dup["id"], content, tags, session_id, embedding)

        now = self._now()
        mid = uuid.uuid4().hex[:12]
        self.conn.execute(
            "INSERT INTO memories (id, content, tags, scope, project_dir, session_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
            (mid, content, json.dumps(tags, ensure_ascii=False), scope, pdir, session_id, now, now)
        )
        self.conn.execute(
            "INSERT INTO vec_memories (id, embedding) VALUES (?, ?)",
            (mid, json.dumps(embedding))
        )
        self.conn.commit()
        return {"id": mid, "action": "created"}

    def update(self, mid: str, content: str, tags: list[str], session_id: int,
               embedding: list[float]) -> dict:
        now = self._now()
        self.conn.execute(
            "UPDATE memories SET content=?, tags=?, session_id=?, updated_at=? WHERE id=?",
            (content, json.dumps(tags, ensure_ascii=False), session_id, now, mid)
        )
        self.conn.execute("DELETE FROM vec_memories WHERE id=?", (mid,))
        self.conn.execute(
            "INSERT INTO vec_memories (id, embedding) VALUES (?, ?)",
            (mid, json.dumps(embedding))
        )
        self.conn.commit()
        return {"id": mid, "action": "updated"}

    def find_duplicate(self, embedding: list[float], threshold: float, project_dir: str = "") -> dict | None:
        rows = self.conn.execute(
            "SELECT id, distance FROM vec_memories WHERE embedding MATCH ? AND k = 5",
            (json.dumps(embedding),)
        ).fetchall()
        for r in rows:
            mem = self.conn.execute("SELECT project_dir FROM memories WHERE id=?", (r["id"],)).fetchone()
            if mem and mem["project_dir"] == project_dir:
                similarity = 1 - (r["distance"] ** 2) / 2
                if similarity >= threshold:
                    return dict(r)
        return None

    def search_by_vector(self, embedding: list[float], top_k: int = 5,
                         scope: str = "all", project_dir: str = "") -> list[dict]:
        k = top_k * 3
        rows = self.conn.execute(
            "SELECT id, distance FROM vec_memories WHERE embedding MATCH ? AND k = ?",
            (json.dumps(embedding), k)
        ).fetchall()
        results = []
        for r in rows:
            mem = self.conn.execute("SELECT * FROM memories WHERE id=?", (r["id"],)).fetchone()
            if not mem:
                continue
            if scope == "project" and mem["project_dir"] != project_dir:
                continue
            if scope == "user" and mem["project_dir"] != USER_SCOPE_DIR:
                continue
            d = dict(mem)
            d["distance"] = r["distance"]
            results.append(d)
            if len(results) >= top_k:
                break
        return results

    def delete(self, mid: str) -> bool:
        cur = self.conn.execute("DELETE FROM memories WHERE id=?", (mid,))
        self.conn.execute("DELETE FROM vec_memories WHERE id=?", (mid,))
        self.conn.commit()
        return cur.rowcount > 0

    def get_by_session_range(self, start: int, end: int, project_dir: str = "") -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE session_id BETWEEN ? AND ? AND project_dir = ? ORDER BY created_at",
            (start, end, project_dir)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all(self, limit: int = 100, offset: int = 0, project_dir: str | None = None) -> list[dict]:
        if project_dir is not None:
            rows = self.conn.execute(
                "SELECT * FROM memories WHERE project_dir = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (project_dir, limit, offset)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM memories ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_by_id(self, mid: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM memories WHERE id=?", (mid,)).fetchone()
        return dict(row) if row else None

    def count(self, project_dir: str | None = None) -> int:
        if project_dir is not None:
            return self.conn.execute("SELECT COUNT(*) FROM memories WHERE project_dir=?", (project_dir,)).fetchone()[0]
        return self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    def list_by_tags(self, tags: list[str], scope: str = "all", project_dir: str = "",
                     limit: int = 100) -> list[dict]:
        sql, params = "SELECT * FROM memories WHERE 1=1", []
        if scope == "project":
            sql += " AND project_dir=?"
            params.append(project_dir)
        elif scope == "user":
            sql += f" AND project_dir=?"
            params.append(USER_SCOPE_DIR)
        for tag in tags:
            sql += " AND tags LIKE ?"
            params.append(f'%"{tag}"%')
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]
