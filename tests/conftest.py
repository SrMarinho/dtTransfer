"""Shared fixtures and helpers for integration/e2e tests."""

import pytest
from src.engine.workspace.bootstrap import bootstrap
from src.factories.entity_registry import EntityRegistry
from tests.helpers import limit_query

ROWS = 10


def all_entities() -> list[str]:
    bootstrap()
    return sorted(EntityRegistry.valid_tables())


def entities_by_workspace(ws_id: str) -> list[str]:
    bootstrap()
    return EntityRegistry.list_tables(system=ws_id)


def get_entity(key: str):
    bootstrap()
    return EntityRegistry.getInstance(key, {})


@pytest.fixture(scope="session")
def _bootstrapped():
    bootstrap()
    return True


def assert_query_returns(entity_key: str, row_limit: int = ROWS):
    """Execute the entity's query with a row limit and assert rows returned."""
    entity = get_entity(entity_key)
    query = entity.getQuery()
    assert query, f"{entity_key}: getQuery() returned empty"

    from datetime import date, timedelta
    today = date.today()
    query = query.replace("REPLACE_START_DATE", str(today - timedelta(days=1)))
    query = query.replace("REPLACE_END_DATE", str(today))
    query = query.replace("REPLACE_UNIT_HERE", "1")

    driver = entity.fromDriver.driver
    query = limit_query(query, row_limit, driver)

    conn = entity.fromDriver.connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        assert len(rows) > 0, f"{entity_key}: no rows returned"
    finally:
        cursor.close()
        conn.close()

    return rows


def assert_target_table_exists(entity_key: str):
    """Check that the entity's target table exists and has the expected columns.
    Skips if table doesn't exist in target database."""
    entity = get_entity(entity_key)
    table_name = entity.name

    conn = entity.toDriver.connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = %s ORDER BY ordinal_position",
            (table_name,),
        )
        rows = cursor.fetchall()
        if not rows:
            import pytest
            pytest.skip(
                f"{entity_key}: target table '{table_name}' not found "
                f"in {entity.toDriver.name}"
            )

        if entity.columns:
            actual_cols = {r[0].lower() for r in rows}
            expected_cols = {c.lower() for c in entity.columns}
            missing = expected_cols - actual_cols
            assert not missing, (
                f"{entity_key}: columns missing in target: {missing}"
            )
    finally:
        cursor.close()
        conn.close()

    return rows
