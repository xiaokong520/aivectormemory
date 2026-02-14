import sys
from aivectormemory.protocol import (
    read_message, write_message, make_result, make_error,
    METHOD_NOT_FOUND, INVALID_PARAMS, INTERNAL_ERROR, SERVER_ERROR
)
from aivectormemory.db import ConnectionManager, init_db
from aivectormemory.embedding.engine import EmbeddingEngine
from aivectormemory.tools import TOOL_DEFINITIONS, TOOL_HANDLERS


class MCPServer:
    def __init__(self, project_dir: str | None = None):
        self.cm = ConnectionManager(project_dir=project_dir)
        self.engine = EmbeddingEngine()
        self._session_id = 0
        self._initialized = False

    def _init_db(self):
        init_db(self.cm.conn)
        row = self.cm.conn.execute(
            "SELECT MAX(session_id) as max_sid FROM memories WHERE project_dir=?",
            (self.cm.project_dir,)
        ).fetchone()
        self._session_id = (row["max_sid"] or 0)

    def handle_initialize(self, req_id, params):
        if not self._initialized:
            self._init_db()
            self._initialized = True
        self._session_id += 1
        print(f"[aivectormemory] Session {self._session_id} started, project={self.cm.project_dir}", file=sys.stderr)
        write_message(make_result(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "aivectormemory", "version": "0.1.1"}
        }))

    def handle_tools_list(self, req_id, params):
        write_message(make_result(req_id, {"tools": TOOL_DEFINITIONS}))

    def handle_tools_call(self, req_id, params):
        name = params.get("name", "")
        args = params.get("arguments", {})
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            write_message(make_error(req_id, METHOD_NOT_FOUND, f"Unknown tool: {name}"))
            return
        try:
            result = handler(args, cm=self.cm, engine=self.engine, session_id=self._session_id)
            write_message(make_result(req_id, {
                "content": [{"type": "text", "text": str(result)}]
            }))
        except ValueError as e:
            write_message(make_error(req_id, INVALID_PARAMS, str(e)))
        except Exception as e:
            print(f"[aivectormemory] Error in {name}: {e}", file=sys.stderr)
            write_message(make_error(req_id, SERVER_ERROR, str(e)))

    def handle_notifications_initialized(self, req_id, params):
        pass

    def run(self):
        handlers = {
            "initialize": self.handle_initialize,
            "notifications/initialized": self.handle_notifications_initialized,
            "tools/list": self.handle_tools_list,
            "tools/call": self.handle_tools_call,
        }
        print("[aivectormemory] MCP Server started (stdio)", file=sys.stderr)
        while True:
            msg = read_message()
            if msg is None:
                break
            method = msg.get("method", "")
            req_id = msg.get("id")
            params = msg.get("params", {})
            handler = handlers.get(method)
            if handler:
                handler(req_id, params)
            elif req_id is not None:
                write_message(make_error(req_id, METHOD_NOT_FOUND, f"Unknown method: {method}"))
        self.cm.close()
        print("[aivectormemory] MCP Server stopped", file=sys.stderr)


def run_server(project_dir: str | None = None):
    server = MCPServer(project_dir=project_dir)
    server.run()
