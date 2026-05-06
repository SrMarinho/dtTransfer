from unittest.mock import MagicMock, call
from src.processes.full_query import FullQuery
from src.processes.params import FullQueryParams


def _make_table(rows=None):
    table = MagicMock()
    table.name = "test_table"
    table.columns = []
    table.getQuery.return_value = "SELECT 1"
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchmany.side_effect = [rows or [(1, "a"), (2, "b")], []]
    conn.cursor.return_value = cursor
    table.fromDriver.connection.return_value = conn
    return table, cursor


def test_run_inserts_rows_from_source():
    table, cursor = _make_table(rows=[(1, "a"), (2, "b")])
    spy_logger = MagicMock()

    process = FullQuery(table, FullQueryParams(), logger=spy_logger)
    result = process.run()

    assert result is True
    table.insert.assert_called_once_with([(1, "a"), (2, "b")])
    assert process.insertedRows == 0  # insertedRows not incremented in FullQuery (uses numOfRows local)


def test_run_truncates_before_insert_when_flag_set():
    table, _ = _make_table()

    process = FullQuery(table, FullQueryParams(truncate=True), logger=MagicMock())
    process.run()

    table.truncate.assert_called_once()


def test_run_does_not_truncate_when_flag_false():
    table, _ = _make_table()

    process = FullQuery(table, FullQueryParams(truncate=False), logger=MagicMock())
    process.run()

    table.truncate.assert_not_called()
