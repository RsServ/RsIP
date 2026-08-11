from __future__ import annotations

from pathlib import Path
import socket

from stem import Signal
from stem.control import Controller

TOR_CONTROL_HOST = "127.0.0.1"
TOR_CONTROL_PORT = 9051
TOR_SOCKS_HOST = "127.0.0.1"
TOR_SOCKS_PORT = 9050
PASSWORD_FILE = Path("/etc/rsip/tor-control-password")


class TorManager:
    def __init__(self) -> None:
        self.host = TOR_CONTROL_HOST
        self.port = TOR_CONTROL_PORT
        self.socks_host = TOR_SOCKS_HOST
        self.socks_port = TOR_SOCKS_PORT
        self.controller = None

    def connect(self) -> None:
        if not self._port_open(self.host, self.port):
            raise RuntimeError(
                "Tor ControlPort is unavailable on 127.0.0.1:9051. "
                "Run the RsiP installer or check the tor service."
            )

        self.controller = Controller.from_port(address=self.host, port=self.port)

        password = None
        if PASSWORD_FILE.exists():
            password = PASSWORD_FILE.read_text(encoding="utf-8").strip()

        try:
            if password:
                self.controller.authenticate(password=password)
            else:
                self.controller.authenticate()
        except Exception as exc:
            self.close()
            raise RuntimeError(f"Tor authentication failed: {exc}") from exc

    def new_identity(self) -> None:
        if self.controller is None:
            self.connect()

        self.controller.signal(Signal.NEWNYM)

    def close(self) -> None:
        if self.controller is not None:
            try:
                self.controller.close()
            except Exception:
                pass
            self.controller = None

    @staticmethod
    def _port_open(host: str, port: int) -> bool:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            return False
