import subprocess
from datetime import datetime, timedelta

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from . import __version__
from .commits import dry_run_preview, make_commit, random_dates, random_dates_range
from .config import get_repo_url, set_repo_url, show_config
from .repo import ensure_repo, pull_repo, push_repo, verify_repo

app = typer.Typer(
    name="greener",
    help="Fill your GitHub contribution graph with custom commits.",
    no_args_is_help=True,
)
console = Console()

COMMIT_DEFAULT = 20
FILE_DEFAULT = "data.txt"
MESSAGE_DEFAULT = "update"


def _print_error(msg: str):
    console.print(f"[red]✖[/red] {msg}")


def _print_success(msg: str):
    console.print(f"[green]✔[/green] {msg}")


def _prompt_for_repo() -> str:
    console.print(
        Panel(
            "[yellow]No repository configured yet.[/yellow]\n"
            "Enter a Git URL to clone, or a local path to an existing repo.",
            title="Setup Required",
        )
    )
    while True:
        url = Prompt.ask("Repo URL or local path")
        if url.strip():
            return url.strip()
        _print_error("Please enter a valid URL or path.")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    commits: int = typer.Option(
        COMMIT_DEFAULT, "--commits", "-n", help="Number of commits to make"
    ),
    days: int = typer.Option(
        None,
        "--days",
        "-d",
        help="Spread commits over the last N days (default: year to date)",
    ),
    start: str = typer.Option(
        None,
        "--start",
        help="Start date (YYYY-MM-DD). Overrides --days.",
    ),
    end: str = typer.Option(
        None,
        "--end",
        help="End date (YYYY-MM-DD). Requires --start.",
    ),
    file: str = typer.Option(
        FILE_DEFAULT, "--file", "-f", help="File to modify for each commit"
    ),
    message: str = typer.Option(
        MESSAGE_DEFAULT, "--message", "-m", help="Commit message"
    ),
    set_repo: str = typer.Option(
        None,
        "--set-repo",
        "-r",
        help="Set or change the stored repo URL and exit",
    ),
    show: bool = typer.Option(
        False,
        "--show-config",
        help="Display current configuration and exit",
    ),
    no_push: bool = typer.Option(
        False,
        "--no-push",
        help="Skip git push after committing",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview commits without making any",
    ),
    version: bool = typer.Option(
        False, "--version", help="Show version and exit.", is_eager=True
    ),
):
    if version:
        console.print(f"greener v{__version__}")
        raise typer.Exit()

    if show:
        cfg = show_config()
        table = Table(title="Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("repo_url", cfg.get("repo_url") or "[dim]not set[/dim]")
        console.print(table)
        raise typer.Exit()

    if set_repo:
        set_repo_url(set_repo)
        _print_success(f"Repo URL set to: {set_repo}")
        repo_path = ensure_repo(set_repo)
        pull_repo(repo_path)
        _print_success(f"Repo cloned/pulled at: {repo_path}")
        raise typer.Exit()

    repo_url = get_repo_url()
    if not repo_url:
        repo_url = _prompt_for_repo()
        set_repo_url(repo_url)
        _print_success("Repo URL saved.")

    repo_path = ensure_repo(repo_url)
    pull_repo(repo_path)
    _print_success(f"Ready at: {repo_path}")

    if start:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d") if end else datetime.now()
        dates = random_dates_range(commits, start_date, end_date)
    elif days is not None:
        dates = random_dates(commits, days)
    else:
        today = datetime.now()
        jan1 = datetime(today.year, 1, 1)
        dates = random_dates(commits, (today - jan1).days)

    if dry_run:
        console.print(dry_run_preview(dates, repo_path, file, message))
        raise typer.Exit()

    with console.status(f"Making [bold]{commits}[/bold] commits...") as status:
        for i, d in enumerate(dates, 1):
            status.update(
                f"[{i}/{commits}] Committing at {d.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            try:
                make_commit(d, repo_path, file, message)
            except subprocess.CalledProcessError as e:
                _print_error(
                    f"Git command failed at commit {i}/{commits}: {e.stderr.decode() if e.stderr else e}"
                )
                raise typer.Exit(code=1)

    _print_success(f"{commits} commits made.")

    if not no_push:
        errors = verify_repo(repo_path)
        if errors:
            _print_error("Repo corruption detected.")
            for err in errors:
                console.print(f"  [red]{err}[/red]")
            console.print(
                "[yellow]Reclone and retry:[/yellow] rm -rf ~/.greener/cache && greener --set-repo <url>"
            )
            raise typer.Exit(code=1)

        with console.status("Pushing to remote..."):
            try:
                push_repo(repo_path)
            except subprocess.CalledProcessError as e:
                msg = e.stderr.decode() if e.stderr else str(e)
                _print_error(f"Push failed: {msg}")
                raise typer.Exit(code=1)
        _print_success("Pushed to remote.")
