from __future__ import annotations

import requests

IP_URL = "https://api.ipify.org"


def get_tor_ip(timeout: int = 15) -> str:
    proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050",
    }

    response = requests.get(
        IP_URL,
        proxies=proxies,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.text.strip()
