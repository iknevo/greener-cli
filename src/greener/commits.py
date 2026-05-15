import os
import random
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Sequence


def random_dates(num_commits: int, days_back: int) -> list[datetime]:
    now = datetime.now()
    start = now - timedelta(days=days_back)
    return _sample_timestamps(start, now, num_commits)


def random_dates_range(
    num_commits: int, start: datetime, end: datetime
) -> list[datetime]:
    return _sample_timestamps(start, end, num_commits)


def _sample_timestamps(start: datetime, end: datetime, n: int) -> list[datetime]:
    total_seconds = int((end - start).total_seconds())
    if total_seconds <= 0:
        return [start] * n
    offsets = sorted(random.randint(0, total_seconds) for _ in range(n))
    return [start + timedelta(seconds=s) for s in offsets]


def make_commit(
    date: datetime,
    repo_path: Path,
    filename: str,
    message: str = "update",
):
    filepath = repo_path / filename
    with open(filepath, "a") as f:
        f.write(f"Commit at {date.isoformat()}\n")
    subprocess.run(
        ["git", "add", filename],
        cwd=str(repo_path),
        capture_output=True,
        check=True,
    )
    env = os.environ.copy()
    date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(repo_path),
        env=env,
        capture_output=True,
        check=True,
    )
    time.sleep(0.02)


def dry_run_preview(dates: Sequence[datetime], repo_path: Path, filename: str, message: str):
    total = len(dates)
    day_counts: dict[str, int] = {}
    for d in dates:
        key = d.strftime("%Y-%m-%d")
        day_counts[key] = day_counts.get(key, 0) + 1

    lines = [
        f"  Repo:     {repo_path}",
        f"  File:     {filename}",
        f"  Message:  {message}",
        f"  Commits:  {total}",
        f"  Span:     {dates[0].strftime('%Y-%m-%d')}  →  {dates[-1].strftime('%Y-%m-%d')}",
        f"  Days w/ commits: {len(day_counts)}",
        "",
    ]
    for day, count in sorted(day_counts.items()):
        bars = "█" * count
        lines.append(f"    {day}  {bars}  {count}")
    return "\n".join(lines)
