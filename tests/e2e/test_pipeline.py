"""E2E tests: full pipeline (extract -> truncate -> insert)."""

import pytest
from tests.conftest import get_entity, assert_query_returns

pytestmark = pytest.mark.e2e


_ENTITIES = [
    # biMktNaz - entidades pequenas (full load viavel)
    "biMktNaz/cliente",
    "biMktNaz/produto",
    # biSenior
    "biSenior/filiais",
    "biSenior/portadores",
    # biNazaria
    "biNazaria/produtos",
]


@pytest.mark.parametrize("entity_key", _ENTITIES)
def test_pipeline_extract_truncate_insert(entity_key):
    rows = assert_query_returns(entity_key, 10)

    entity = get_entity(entity_key)
    entity.truncate()
    entity.insert(rows)

    conn = entity.toDriver.connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {entity.name}")
        count = cursor.fetchone()[0]
        assert count == len(rows), (
            f"{entity_key}: expected {len(rows)} rows, got {count}"
        )
    finally:
        cursor.close()
        conn.close()
