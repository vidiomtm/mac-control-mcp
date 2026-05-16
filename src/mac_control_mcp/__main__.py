import logging
import sys

logging.basicConfig(
    stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(name)s %(message)s"
)


def main() -> None:
    from mac_control_mcp.server import create_server

    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
