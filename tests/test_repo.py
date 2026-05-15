from greener.repo import sanitize_url, is_local_path


def test_sanitize_https_url():
    result = sanitize_url("https://github.com/user/repo.git")
    assert "user" in result
    assert "repo" in result


def test_sanitize_ssh_url():
    result = sanitize_url("git@github.com:user/repo.git")
    assert "github.com" in result
    assert "user" in result
    assert "repo" in result


def test_sanitize_https_without_git_suffix():
    result = sanitize_url("https://github.com/user/repo")
    assert "user" in result
    assert "repo" in result


def test_sanitize_consistency():
    ssh = sanitize_url("git@github.com:user/repo.git")
    https = sanitize_url("https://github.com/user/repo.git")
    assert ssh == https


def test_is_local_path_returns_false_for_url():
    assert not is_local_path("https://github.com/user/repo.git")


def test_is_local_path_returns_true_for_existing_dir(tmp_path):
    assert is_local_path(str(tmp_path))
