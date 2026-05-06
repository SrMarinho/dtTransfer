import pytest
from src.core.entity import filter_columns


def test_no_columns_returns_rows_unchanged():
    rows = [(1, "a"), (2, "b")]
    desc = [("id",), ("nome",)]
    assert filter_columns([], rows, desc) is rows


def test_select_subset_by_name():
    rows = [(1, "joao", "123"), (2, "maria", "456")]
    desc = [("id",), ("nome",), ("cpf",)]
    result = filter_columns(["nome", "id"], rows, desc)
    assert result == [["joao", 1], ["maria", 2]]


def test_reorder_columns():
    rows = [(1, "joao", "123")]
    desc = [("id",), ("nome",), ("cpf",)]
    result = filter_columns(["cpf", "nome"], rows, desc)
    assert result == [["123", "joao"]]


def test_single_column():
    rows = [(1, "joao"), (2, "maria")]
    desc = [("id",), ("nome",)]
    result = filter_columns(["nome"], rows, desc)
    assert result == [["joao"], ["maria"]]


def test_case_insensitive_column_name():
    rows = [(1, "joao")]
    desc = [("ID",), ("NOME",)]
    result = filter_columns(["id", "nome"], rows, desc)
    assert result == [[1, "joao"]]


def test_fallback_on_missing_column():
    """Positional fallback when column name is not found in description."""
    rows = [(1, "joao")]
    desc = [("id",), ("nome",)]
    result = filter_columns(["xpto"], rows, desc)
    assert result == [[1]]


def test_empty_rows_returns_empty():
    rows = []
    desc = [("id",), ("nome",)]
    result = filter_columns(["id"], rows, desc)
    assert result == []


def test_all_columns_explicitly():
    rows = [(1, "joao")]
    desc = [("id",), ("nome",)]
    result = filter_columns(["id", "nome"], rows, desc)
    assert result == [[1, "joao"]]


def test_null_values_preserved():
    rows = [(1, None), (2, "joao")]
    desc = [("id",), ("nome",)]
    result = filter_columns(["nome", "id"], rows, desc)
    assert result == [[None, 1], ["joao", 2]]
