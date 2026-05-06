"""ProcessFactory edge cases: _to_bool, _parse_* with missing/malformed params."""
import pytest
from src.factories.process_factory import _to_bool, _parse_full, _parse_incremental, _parse_monthly, _parse_unit
from src.processes.params import FullQueryParams, IncrementalParams, MonthlyParams, UnitParams


class TestToBool:
    def test_true_literals(self):
        assert _to_bool(True) is True
        assert _to_bool(False) is False

    def test_string_true(self):
        assert _to_bool("true") is True
        assert _to_bool("True") is True
        assert _to_bool("TRUE") is True

    def test_string_false(self):
        assert _to_bool("false") is False
        assert _to_bool("False") is False
        assert _to_bool("anything") is False
        assert _to_bool("") is False


class TestParseFull:
    def test_defaults(self):
        p = _parse_full({})
        assert isinstance(p, FullQueryParams)
        assert p.truncate is False

    def test_truncate_true(self):
        p = _parse_full({"truncate": True})
        assert p.truncate is True

    def test_truncate_string_true(self):
        p = _parse_full({"truncate": "true"})
        assert p.truncate is True

    def test_truncate_missing(self):
        p = _parse_full({"other": "x"})
        assert p.truncate is False


class TestParseIncremental:
    def test_defaults(self):
        p = _parse_incremental({})
        assert p.days is None
        assert p.threads == 4
        assert p.truncate is False
        assert p.current_day is False
        assert p.full is False

    def test_days_zero(self):
        p = _parse_incremental({"days": 0})
        assert p.days == 0

    def test_days_string(self):
        p = _parse_incremental({"days": "7"})
        assert p.days == 7

    def test_days_none(self):
        p = _parse_incremental({"days": None})
        assert p.days is None

    def test_threads_string(self):
        p = _parse_incremental({"threads": "8"})
        assert p.threads == 8

    def test_full_string(self):
        p = _parse_incremental({"full": "true"})
        assert p.full is True

    def test_current_day_string(self):
        p = _parse_incremental({"currentDay": "true"})
        assert p.current_day is True

    def test_all_flags(self):
        p = _parse_incremental({"days": 5, "threads": 2, "truncate": True, "currentDay": True, "full": False})
        assert p.days == 5
        assert p.threads == 2
        assert p.truncate is True
        assert p.current_day is True
        assert p.full is False


class TestParseMonthly:
    def test_defaults(self):
        p = _parse_monthly({})
        assert p.months is None
        assert p.method == "byMonth"
        assert p.truncate is False
        assert p.full is False

    def test_months_zero(self):
        p = _parse_monthly({"months": 0})
        assert p.months == 0

    def test_months_string(self):
        p = _parse_monthly({"months": "3"})
        assert p.months == 3

    def test_method_whole(self):
        p = _parse_monthly({"method": "wholeInterval"})
        assert p.method == "wholeInterval"

    def test_custom_method(self):
        p = _parse_monthly({"method": "unknown"})
        assert p.method == "unknown"


class TestParseUnit:
    def test_defaults(self):
        p = _parse_unit({})
        assert p.unit == 0

    def test_unit_value(self):
        p = _parse_unit({"unit": 5})
        assert p.unit == 5

    def test_unit_string(self):
        p = _parse_unit({"unit": "3"})
        assert p.unit == 3
