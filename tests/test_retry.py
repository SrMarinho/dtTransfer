import threading
import pytest
from unittest.mock import MagicMock
from src.processes.retry import connect_with_retry


def _driver(fail_times=0):
    calls = {"n": 0}
    mock = MagicMock()

    def connection():
        calls["n"] += 1
        if calls["n"] <= fail_times:
            raise Exception("connection refused")
        return MagicMock(name="conn")

    mock.connection = connection
    return mock


def test_connects_on_first_try():
    conn = connect_with_retry(_driver(0), "t", threading.Event(), base_delay=0, max_delay=0)
    assert conn is not None


def test_retries_and_succeeds():
    conn = connect_with_retry(_driver(2), "t", threading.Event(), max_tries=3, base_delay=0, max_delay=0)
    assert conn is not None


def test_returns_none_when_exhausted():
    conn = connect_with_retry(_driver(99), "t", threading.Event(), max_tries=3, base_delay=0, max_delay=0)
    assert conn is None


def test_returns_none_when_stopped():
    stop = threading.Event()
    stop.set()
    conn = connect_with_retry(_driver(1), "t", stop, max_tries=3, base_delay=0, max_delay=0)
    assert conn is None
