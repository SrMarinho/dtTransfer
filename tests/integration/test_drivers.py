import pytest
from src.engine.workspace.bootstrap import bootstrap
from src.factories.database_factory import Database, DatabaseFactory


bootstrap()


@pytest.mark.integration
@pytest.mark.parametrize("db_enum", [
    Database.BIMKTNAZ,
    Database.BISENIOR,
    Database.BINAZARIA,
    Database.PBSNAZARIADADOS,
    Database.SENIOR,
])
def test_driver_connects(db_enum):
    """Test that each database driver can establish a connection"""
    driver = DatabaseFactory.getInstance(db_enum)
    conn = driver.connection()
    cursor = conn.cursor()

    try:
        # Oracle requires FROM DUAL for SELECT without a table
        if db_enum == Database.SENIOR:
            cursor.execute("SELECT 1 FROM DUAL")
        else:
            cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result is not None, f"Database {db_enum.value} did not return result from SELECT 1"
    finally:
        cursor.close()
        conn.close()
