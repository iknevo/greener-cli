from pathlib import Path

import pytest

from greener.config import get_repo_url, load_config, save_config, set_repo_url


@pytest.fixture(autouse=True)
def temp_config_dir(monkeypatch, tmp_path):
    cfg_dir = tmp_path / ".greener"
    monkeypatch.setattr("greener.config.CONFIG_DIR", cfg_dir)
    monkeypatch.setattr("greener.config.CONFIG_PATH", cfg_dir / "config.json")
    monkeypatch.setattr("greener.config.CACHE_DIR", cfg_dir / "cache")


def test_save_and_load_config():
    save_config({"repo_url": "git@github.com:user/repo.git"})
    cfg = load_config()
    assert cfg["repo_url"] == "git@github.com:user/repo.git"


def test_load_config_empty_when_no_file():
    cfg = load_config()
    assert cfg == {}


def test_set_and_get_repo_url():
    set_repo_url("https://github.com/user/repo.git")
    assert get_repo_url() == "https://github.com/user/repo.git"


def test_get_repo_url_none_when_not_set():
    assert get_repo_url() is None


def test_set_repo_url_overwrites():
    set_repo_url("https://github.com/user/first.git")
    set_repo_url("https://github.com/user/second.git")
    assert get_repo_url() == "https://github.com/user/second.git"
