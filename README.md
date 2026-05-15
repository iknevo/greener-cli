# greener

Fill your GitHub contribution graph with custom, backdated commits.

> **⚠️ Disclaimer**
>
> This tool creates fake commit activity to manipulate your GitHub contribution graph. This is a **violation of GitHub's Terms of Service** and may result in your account being **suspended or banned**. Use at your own risk. This project is for educational purposes only.

## Install

Requires Python 3.10+ and Git.

### macOS / Linux

```bash
pip install git+ssh://git@github.com/iknevo/greener-cli.git
```

Or with pipx (recommended to avoid environment conflicts):

```bash
pipx install git+ssh://git@github.com/iknevo/greener-cli.git
```

### Windows

```powershell
pip install git+https://github.com/iknevo/greener-cli.git
```

Or with pipx (recommended):

```powershell
pipx install git+https://github.com/iknevo/greener-cli.git
```

> **Note:** If `pipx` is not installed on Windows, install it with `pip install pipx` then add `%USERPROFILE%\.local\bin` to your PATH.

## Usage

```bash
# First time — set up a repo
greener --set-repo git@github.com:user/repo.git

# 50 commits from Jan 1 → today (default date range)
greener -n 50

# 20 commits in the last 7 days
greener -n 20 -d 7

# 10 commits in a custom date range
greener -n 10 --start 2024-06-01 --end 2024-12-01

# Preview without writing anything
greener -n 50 -d 30 --dry-run

# Custom file and message, skip push
greener -n 10 -d 7 -f log.md -m "update" --no-push

# Show current config
greener --show-config
```

## How it works

- **No repo configured** — prompts you for a Git URL or local path, saves it, and runs immediately
- **No `--days` given** — defaults to the full current year (Jan 1 → today)
- **URL** — cloned to `~/.greener/cache/<host_path>/` and reused on later runs
- **Local path** — used in-place
- Commits are **backdated with random timestamps** within the time window. Some days get multiple commits, some get none — natural-looking activity.
- After committing, `git pull --rebase` then `git push` to the remote (skipped with `--no-push`)

## All options

| Flag | Default | Description |
|------|---------|-------------|
| `-n, --commits` | `20` | Number of commits |
| `-d, --days` | year-to-date | Spread over last N days |
| `--start --end` | — | Explicit date range (overrides `--days`) |
| `-f, --file` | `data.txt` | File to modify |
| `-m, --message` | `update` | Commit message |
| `-r, --set-repo` | — | Set stored repo URL and exit |
| `--show-config` | — | Display current configuration |
| `--no-push` | — | Skip `git push` |
| `--dry-run` | — | Preview without making commits |
| `--version` | — | Show version |

## Development

```bash
git clone git@github.com:iknevo/greener-cli.git
cd greener-cli

python -m venv venv
source venv/bin/activate
pip install -e .
pip install pytest

greener --help

python -m pytest tests/
```

## License

MIT
