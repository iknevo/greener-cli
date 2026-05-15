import json
from pathlib import Path


CONFIG_DIR = Path.home() / ".greener"
CONFIG_PATH = CONFIG_DIR / "config.json"
CACHE_DIR = CONFIG_DIR / "cache"


def ensure_dirs():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text())


def save_config(data: dict):
    ensure_dirs()
    CONFIG_PATH.write_text(json.dumps(data, indent=2))


def get_repo_url() -> str | None:
    return load_config().get("repo_url")


def set_repo_url(url: str):
    save_config({"repo_url": url})


def show_config() -> dict:
    cfg = load_config()
    if not cfg:
        return {"repo_url": None}
    return cfg
