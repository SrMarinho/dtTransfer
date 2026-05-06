from unittest.mock import MagicMock, patch
import time
from src.processes.incremental import Incremental
from src.processes.monthly import Monthly
from src.processes.params import IncrementalParams, MonthlyParams


def _make_table(query="SELECT 1"):
    mock_table = MagicMock()
    mock_table.name = "fake_table"
    mock_table.getQuery.return_value = query
    return mock_table


def test_incremental_calls_on_progress():
    calls = []

    def on_progress(current, total):
        calls.append((current, total))

    table = _make_table()
    params = IncrementalParams(days=3)

    with patch.object(Incremental, "oneDay"):
        process = Incremental(table, params, on_progress=on_progress)
        process.run()

    assert len(calls) == 3
    assert calls[-1] == (3, 3)


def test_incremental_no_on_progress_does_not_fail():
    table = _make_table()
    params = IncrementalParams(days=2)

    with patch.object(Incremental, "oneDay"):
        process = Incremental(table, params)
        process.run()  # must not raise


def test_monthly_calls_on_progress():
    calls = []

    def on_progress(current, total):
        calls.append((current, total))

    table = _make_table()
    params = MonthlyParams(months=2)

    time_counter = {"value": 100.0}

    def mock_time_func():
        result = time_counter["value"]
        time_counter["value"] += 0.1
        return result

    with patch.object(Monthly, "oneMonth"), \
         patch("src.processes.monthly.time.time", side_effect=mock_time_func):
        process = Monthly(table, params, on_progress=on_progress)
        process.byMonth()

    assert len(calls) == 2
    assert calls[-1] == (2, 2)
