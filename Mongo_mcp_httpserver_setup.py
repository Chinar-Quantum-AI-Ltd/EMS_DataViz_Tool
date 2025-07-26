import subprocess
import socket
import time
import os
from dotenv import load_dotenv


load_dotenv()

uri = os.getenv("MDB_MCP_CONNECTION_STRING")

def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False

def start_mcp_http_server(mongo_uri=uri, host="127.0.0.1", port=3000):
    if is_port_open(host, port):
        print(f" MCP server already running at http://{host}:{port}")
        return

    print(" Starting MCP server...")

    npx_path = "C:\\Program Files\\nodejs\\npx.cmd"
    subprocess.Popen(
        [
            npx_path, "-y", "mongodb-mcp-server",
            "--transport", "http",
            "--httpHost", host,
            "--httpPort", str(port),
            "--readOnly"
        ],
        env={**os.environ, "MDB_MCP_CONNECTION_STRING": mongo_uri},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for server to start
    for _ in range(15):
        if is_port_open(host, port):
            print("MCP server is ready")
            return
        time.sleep(1)

    raise RuntimeError("MCP HTTP server failed to start")
