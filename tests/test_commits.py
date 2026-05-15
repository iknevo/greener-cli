from datetime import datetime, timedelta

from greener.commits import random_dates, random_dates_range


def test_random_dates_returns_correct_count():
    dates = random_dates(50, 30)
    assert len(dates) == 50


def test_random_dates_within_window():
    dates = random_dates(100, 7)
    now = datetime.now()
    cutoff = now - timedelta(days=7)
    for d in dates:
        assert cutoff <= d <= now


def test_random_dates_sorted():
    dates = random_dates(20, 10)
    for i in range(1, len(dates)):
        assert dates[i - 1] <= dates[i]


def test_random_dates_range_returns_correct_count():
    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31)
    dates = random_dates_range(30, start, end)
    assert len(dates) == 30


def test_random_dates_range_within_bounds():
    start = datetime(2024, 6, 1)
    end = datetime(2024, 6, 30)
    dates = random_dates_range(50, start, end)
    for d in dates:
        assert start <= d <= end


def test_random_dates_zero_window():
    dates = random_dates(5, 0)
    assert len(dates) == 5
    now = datetime.now()
    for d in dates:
        assert abs((d - now).total_seconds()) < 1


def test_random_dates_range_zero_window():
    now = datetime.now()
    dates = random_dates_range(5, now, now)
    for d in dates:
        assert d == now
