"""Launcher script for packaging Streamlit app with PyInstaller."""
import sys
import os
import signal
import socket
import threading
import time
from pathlib import Path

import webview

# Monkey-patch signal.signal so Streamlit can run in a non-main thread
# without crashing on "signal only works in main thread" ValueError.
_original_signal = signal.signal


def _safe_signal(signum, handler):
    try:
        return _original_signal(signum, handler)
    except ValueError:
        return signal.SIG_DFL


signal.signal = _safe_signal


def _find_free_port() -> int:
    """Find an available TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 30.0) -> bool:
    """Block until Streamlit server is accepting connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _start_streamlit(app_script: str, port: int):
    """Run Streamlit server in a background thread."""
    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        app_script,
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]
    stcli.main()


def main():
    # When running as a PyInstaller bundle, sys._MEIPASS points to the temp dir
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    # Change working directory so relative paths (e.g. "assets/lot.png") work
    os.chdir(base_path)

    app_script = str(base_path / "app.py")
    port = _find_free_port()

    # Start Streamlit in a daemon thread
    server_thread = threading.Thread(
        target=_start_streamlit, args=(app_script, port), daemon=True
    )
    server_thread.start()

    # Wait for the server to be ready
    if not _wait_for_server(port):
        print("Error: Streamlit server failed to start.")
        sys.exit(1)

    # Open a native window pointing to the Streamlit app
    webview.create_window(
        "今天吃什麼",
        f"http://127.0.0.1:{port}",
        width=1100,
        height=750,
    )
    webview.start()


if __name__ == "__main__":
    main()
