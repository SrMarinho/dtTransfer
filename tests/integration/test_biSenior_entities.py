"""Integration tests: query execution for all biSenior entities."""

import pytest
from tests.conftest import entities_by_workspace, assert_query_returns, assert_target_table_exists

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("entity", entities_by_workspace("biSenior"))
def test_biSenior_query_returns_rows(entity):
    assert_query_returns(entity)


@pytest.mark.parametrize("entity", entities_by_workspace("biSenior"))
def test_biSenior_target_table_exists(entity):
    assert_target_table_exists(entity)
