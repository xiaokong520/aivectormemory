import argparse
import sys


def main():
    parser = argparse.ArgumentParser(prog="run", description="AIVectorMemory MCP Server")
    parser.add_argument("--project-dir", default=None, help="项目根目录，默认当前目录")
    sub = parser.add_subparsers(dest="command")

    web_parser = sub.add_parser("web", help="启动 Web 看板")
    web_parser.add_argument("--port", type=int, default=9080, help="Web 看板端口")
    web_parser.add_argument("--project-dir", dest="web_project_dir", default=None)

    install_parser = sub.add_parser("install", help="为当前项目配置 MCP")
    install_parser.add_argument("--project-dir", dest="install_project_dir", default=None)

    args = parser.parse_args()

    if args.command == "web":
        project_dir = args.web_project_dir or args.project_dir
        from aivectormemory.web.app import run_web
        run_web(project_dir=project_dir, port=args.port)
    elif args.command == "install":
        project_dir = args.install_project_dir or args.project_dir
        from aivectormemory.install import run_install
        run_install(project_dir)
    else:
        from aivectormemory.server import run_server
        run_server(project_dir=args.project_dir)


if __name__ == "__main__":
    main()
