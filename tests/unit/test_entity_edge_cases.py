"""Entity edge cases: truncate, deleteDay, existsTable, insert failures."""
from unittest.mock import MagicMock
import pytest
from src.core.entity import Entity
from src.factories.database_factory import Database


class _ConcreteEntity(Entity):
    def __init__(self, params=None):
        super().__init__(params)
        self.name = 'test_ent'
        self.columns = ['id', 'val']
        self.fromDB = Database.FAKEDATABASE
        self.toDB = Database.FAKEDATABASE


def _with_driver(entity, driver_mock):
    entity._toDriver = driver_mock
    entity._fromDriver = driver_mock


def test_exists_table_returns_true():
    ent = _ConcreteEntity({})
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = [True]
    fake_conn.cursor.return_value = fake_cursor
    driver = MagicMock()
    driver.connection.return_value = fake_conn
    _with_driver(ent, driver)

    assert ent.existsTable() is True
    fake_cursor.execute.assert_called_once()
    sql = fake_cursor.execute.call_args[0][0]
    assert 'information_schema.tables' in sql


def test_exists_table_returns_false_on_error():
    ent = _ConcreteEntity({})
    driver = MagicMock()
    driver.connection.side_effect = Exception('no db')
    _with_driver(ent, driver)

    assert ent.existsTable() is False


def test_truncate_executes_delete():
    ent = _ConcreteEntity({})
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    driver = MagicMock()
    driver.connection.return_value = fake_conn
    _with_driver(ent, driver)

    ent.truncate()
    fake_cursor.execute.assert_called_once_with('DELETE FROM test_ent')
    fake_conn.commit.assert_called_once()


def test_truncate_swallows_exception():
    ent = _ConcreteEntity({})
    driver = MagicMock()
    driver.connection.side_effect = Exception('conn failed')
    _with_driver(ent, driver)

    ent.truncate()  # must not raise


def test_delete_day_is_noop():
    ent = _ConcreteEntity({})
    result = ent.deleteDay('2025-01-01', '2025-01-02')
    assert result is None


def test_insert_empty_rows_returns_early():
    ent = _ConcreteEntity({})
    driver = MagicMock()
    _with_driver(ent, driver)
    ent.insert([])
    driver.connection.assert_not_called()


def test_insert_raises_on_connection_failure():
    ent = _ConcreteEntity({})
    driver = MagicMock()
    driver.connection.side_effect = Exception('conn down')
    _with_driver(ent, driver)
    with pytest.raises(Exception, match='conn down'):
        ent.insert([(1, 'a')])


def test_table_class_remains_importable():
    from src.core.entity import Entity
    from src.engine.entity import Table
    assert Table is Entity
