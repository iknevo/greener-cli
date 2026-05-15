import re
import subprocess
from pathlib import Path

from .config import CACHE_DIR


GIT_SSH_PATTERN = re.compile(r"git@([^:]+):(.+)\.git$")
GIT_HTTPS_PATTERN = re.compile(r"https?://([^/]+)/(.+?)(?:\.git)?$")


def sanitize_url(url: str) -> str:
    url = url.strip()
    m = GIT_SSH_PATTERN.match(url)
    if m:
        return f"{m.group(1)}_{m.group(2).replace('/', '_')}"
    m = GIT_HTTPS_PATTERN.match(url)
    if m:
        return f"{m.group(1)}_{m.group(2).replace('/', '_')}"
    return url.replace(":", "_").replace("/", "_").replace("@", "_")


def is_local_path(url_or_path: str) -> bool:
    return Path(url_or_path).exists()


def clone_repo(url: str) -> Path:
    safe = sanitize_url(url)
    dest = CACHE_DIR / safe
    if dest.exists():
        return dest
    subprocess.run(
        ["git", "clone", url, str(dest)],
        capture_output=True,
        check=True,
    )
    return dest


def ensure_repo(url_or_path: str) -> Path:
    if is_local_path(url_or_path):
        return Path(url_or_path).resolve()
    return clone_repo(url_or_path)


def pull_repo(path: Path):
    subprocess.run(
        ["git", "pull"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )


def push_repo(path: Path):
    subprocess.run(
        ["git", "pull", "--rebase"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "push"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )


def verify_repo(path: Path) -> list[str]:
    result = subprocess.run(
        ["git", "fsck"],
        cwd=str(path),
        capture_output=True,
        text=True,
    )
    errors = [l for l in result.stdout.splitlines() if l.strip()]
    return errors


def get_remote_url(path: Path) -> str | None:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=str(path),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None
