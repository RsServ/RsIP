from pathlib import Path
import json

CONFIG_DIR = Path.home() / ".config" / "rsip"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "interval": 10,
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        interval = int(data.get("interval", DEFAULT_CONFIG["interval"]))
        return {"interval": max(1, interval)}
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_interval(interval: int) -> None:
    if interval < 1:
        raise ValueError("interval must be >= 1 second")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps({"interval": interval}, indent=2) + "\n",
        encoding="utf-8",
    )
