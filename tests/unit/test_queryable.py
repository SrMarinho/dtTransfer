from unittest.mock import patch, MagicMock
import pytest
from src.core.entity import Entity
from src.factories.database_factory import Database


class ConcreteQueryable(Entity):
    def __init__(self, params):
        super().__init__(params)
        self.fromDB = Database.FAKEDATABASE
        self.toDB = Database.FAKEDATABASE
        self.name = 'test_table'
        self.columns = ['id', 'name']


class TestQueryableLazyLoading:
    def test_driver_not_instantiated_on_init(self):
        """fromDriver and toDriver should not be instantiated until first access"""
        with patch('src.core.entity.DatabaseFactory.getInstance') as mock:
            entity = ConcreteQueryable({})
            mock.assert_not_called()

    def test_from_driver_lazy_on_first_access(self):
        """fromDriver should instantiate on first access"""
        fake = MagicMock()
        with patch('src.core.entity.DatabaseFactory.getInstance', return_value=fake):
            entity = ConcreteQueryable({})
            result = entity.fromDriver
            assert result is fake

    def test_from_driver_cached(self):
        """fromDriver should cache and reuse the same instance"""
        fake = MagicMock()
        with patch('src.core.entity.DatabaseFactory.getInstance', return_value=fake) as mock:
            entity = ConcreteQueryable({})
            first = entity.fromDriver
            second = entity.fromDriver
            assert first is second
            assert mock.call_count == 1, "getInstance should be called only once"

    def test_to_driver_lazy_on_first_access(self):
        """toDriver should instantiate on first access"""
        fake = MagicMock()
        with patch('src.core.entity.DatabaseFactory.getInstance', return_value=fake):
            entity = ConcreteQueryable({})
            result = entity.toDriver
            assert result is fake

    def test_to_driver_cached(self):
        """toDriver should cache and reuse the same instance"""
        fake = MagicMock()
        with patch('src.core.entity.DatabaseFactory.getInstance', return_value=fake) as mock:
            entity = ConcreteQueryable({})
            first = entity.toDriver
            second = entity.toDriver
            assert first is second
            assert mock.call_count == 1, "getInstance should be called only once"

    def test_from_and_to_driver_independent(self):
        """fromDriver and toDriver should be independent instances"""
        fake_from = MagicMock(name='fromDriver')
        fake_to = MagicMock(name='toDriver')
        with patch('src.core.entity.DatabaseFactory.getInstance', side_effect=[fake_from, fake_to]):
            entity = ConcreteQueryable({})
            assert entity.fromDriver is fake_from
            assert entity.toDriver is fake_to

    def test_factory_called_with_correct_database_enum(self):
        """DatabaseFactory.getInstance should be called with the correct Database enum"""
        with patch('src.core.entity.DatabaseFactory.getInstance') as mock:
            mock.return_value = MagicMock()
            entity = ConcreteQueryable({})
            _ = entity.fromDriver
            mock.assert_called_with(Database.FAKEDATABASE)

