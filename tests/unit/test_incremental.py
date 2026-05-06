from unittest.mock import MagicMock, patch
from datetime import date
from src.processes.incremental import Incremental
from src.processes.params import IncrementalParams


def _make_table():
    table = MagicMock()
    table.name = "test_table"
    table.columns = []
    table.getQuery.return_value = "SELECT * WHERE dt BETWEEN REPLACE_START_DATE AND REPLACE_END_DATE"
    return table


FIXED_TODAY = date(2024, 6, 15)


def test_run_processes_correct_number_of_days():
    table = _make_table()
    params = IncrementalParams(days=3)

    with patch.object(Incremental, "oneDay") as mock_oneday:
        process = Incremental(table, params, today_fn=lambda: FIXED_TODAY)
        process.run()

    assert mock_oneday.call_count == 3


def test_run_includes_current_day_when_flag_set():
    table = _make_table()
    params = IncrementalParams(days=2, current_day=True)

    called_days = []

    def capture_day(tbl, query, day):
        called_days.append(day)

    with patch.object(Incremental, "oneDay", side_effect=capture_day):
        process = Incremental(table, params, today_fn=lambda: FIXED_TODAY)
        process.run()

    assert FIXED_TODAY in called_days
    assert len(called_days) == 2


def test_run_excludes_current_day_by_default():
    table = _make_table()
    params = IncrementalParams(days=2, current_day=False)

    called_days = []

    def capture_day(tbl, query, day):
        called_days.append(day)

    with patch.object(Incremental, "oneDay", side_effect=capture_day):
        process = Incremental(table, params, today_fn=lambda: FIXED_TODAY)
        process.run()

    assert FIXED_TODAY not in called_days


def test_run_truncates_before_processing():
    table = _make_table()
    params = IncrementalParams(days=1, truncate=True)

    with patch.object(Incremental, "oneDay"):
        process = Incremental(table, params, today_fn=lambda: FIXED_TODAY)
        process.run()

    table.truncate.assert_called_once()


def test_run_full_skips_date_filtering():
    table = _make_table()
    params = IncrementalParams(full=True)

    with patch.object(Incremental, "_run_full") as mock_full:
        process = Incremental(table, params, today_fn=lambda: FIXED_TODAY)
        process.run()

    mock_full.assert_called_once()
