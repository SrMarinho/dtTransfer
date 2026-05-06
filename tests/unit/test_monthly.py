from unittest.mock import MagicMock, patch
from datetime import date
from src.processes.monthly import Monthly
from src.processes.params import MonthlyParams


def _make_table():
    table = MagicMock()
    table.name = "test_table"
    table.columns = []
    table.getQuery.return_value = "SELECT * WHERE dt BETWEEN REPLACE_START_DATE AND REPLACE_END_DATE"
    return table


FIXED_TODAY = date(2024, 6, 15)


def test_bymonth_processes_correct_number_of_months():
    table = _make_table()
    params = MonthlyParams(months=3)

    with patch.object(Monthly, "oneMonth") as mock_onemonth:
        process = Monthly(table, params, today_fn=lambda: FIXED_TODAY)
        process.byMonth()

    assert mock_onemonth.call_count == 3


def test_bymonth_calls_on_progress():
    calls = []

    def on_progress(current, total):
        calls.append((current, total))

    table = _make_table()
    params = MonthlyParams(months=2)

    with patch.object(Monthly, "oneMonth"):
        process = Monthly(table, params, on_progress=on_progress, today_fn=lambda: FIXED_TODAY)
        process.byMonth()

    assert len(calls) == 2
    assert calls[-1] == (2, 2)


def test_wholeinterval_executes_single_query():
    table = _make_table()
    params = MonthlyParams(months=2)

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchmany.side_effect = [[(1,)], []]
    mock_conn.cursor.return_value = mock_cursor

    with patch("src.processes.monthly.connect_with_retry", return_value=mock_conn):
        process = Monthly(table, params, today_fn=lambda: FIXED_TODAY)
        process.wholeInterval()

    table.deleteMonth.assert_called_once()
    mock_cursor.execute.assert_called_once()
    table.insert.assert_called_once_with([(1,)])
