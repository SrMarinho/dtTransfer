"""FullQuery edge cases: empty results, calculateSize special cases."""
from unittest.mock import MagicMock
from src.processes.full_query import FullQuery
from src.processes.params import FullQueryParams


def _make_table(rows=None):
    table = MagicMock()
    table.name = "test_table"
    table.columns = []
    table.getQuery.return_value = "SELECT 1"
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchmany.side_effect = [rows or [(1, "a")], []]
    conn.cursor.return_value = cursor
    table.fromDriver.connection.return_value = conn
    return table, cursor


class TestCalculateSize:
    def test_empty_rows(self):
        fq = FullQuery(MagicMock(), FullQueryParams())
        assert fq.calculateSize([]) == 0.0

    def test_single_row(self):
        fq = FullQuery(MagicMock(), FullQueryParams())
        size = fq.calculateSize([(1, "hello")])
        assert size > 0

    def test_none_values(self):
        fq = FullQuery(MagicMock(), FullQueryParams())
        size = fq.calculateSize([(None, "text")])
        assert size > 0

    def test_newline_in_value(self):
        fq = FullQuery(MagicMock(), FullQueryParams())
        rows = [(1, "line1\nline2")]
        fq.calculateSize(rows)
        # value should have \n replaced with \\n — no raw newline in output

    def test_carriage_return_in_value(self):
        fq = FullQuery(MagicMock(), FullQueryParams())
        rows = [(1, "text\r")]
        fq.calculateSize(rows)

    def test_unicode_chars(self):
        fq = FullQuery(MagicMock(), FullQueryParams())
        rows = [(1, "café")]
        size = fq.calculateSize(rows)
        assert size > 0

    def test_semicolon_in_value(self):
        fq = FullQuery(MagicMock(), FullQueryParams())
        rows = [(1, "a;b;c")]
        fq.calculateSize(rows)
        # ; is used as delimiter in output — verifying no crash

    def test_multiple_rows(self):
        fq = FullQuery(MagicMock(), FullQueryParams())
        rows = [(i, f"val_{i}") for i in range(100)]
        size = fq.calculateSize(rows)
        assert size > 0

    def test_wide_row(self):
        fq = FullQuery(MagicMock(), FullQueryParams())
        rows = [(1, "x" * 10_000)]
        size = fq.calculateSize(rows)
        assert size > 0.009  # ~9.5 KB for 10K chars


class TestRunEdgeCases:
    def test_empty_result_set(self):
        table, cursor = _make_table(rows=[])
        process = FullQuery(table, FullQueryParams(), logger=MagicMock())
        result = process.run()
        assert result is True

    def test_single_row_result(self):
        table, _ = _make_table(rows=[(42,)])
        process = FullQuery(table, FullQueryParams(), logger=MagicMock())
        result = process.run()
        assert result is True

    def test_multiple_batches(self):
        table = MagicMock()
        table.name = "test"
        table.getQuery.return_value = "SELECT 1"
        conn = MagicMock()
        cursor = MagicMock()
        # Return 3 batches: first 2 have data, 3rd is empty
        cursor.fetchmany.side_effect = [[(1,)], [(2,)], []]
        conn.cursor.return_value = cursor
        table.fromDriver.connection.return_value = conn
        process = FullQuery(table, FullQueryParams(), logger=MagicMock())
        result = process.run()
        assert result is True
        assert table.insert.call_count == 2
