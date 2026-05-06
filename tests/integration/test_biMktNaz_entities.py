"""Integration tests: query execution for all biMktNaz entities."""

import pytest
from tests.conftest import entities_by_workspace, assert_query_returns, assert_target_table_exists

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("entity", entities_by_workspace("biMktNaz"))
def test_biMktNaz_query_returns_rows(entity):
    assert_query_returns(entity)


@pytest.mark.parametrize("entity", entities_by_workspace("biMktNaz"))
def test_biMktNaz_target_table_exists(entity):
    assert_target_table_exists(entity)
